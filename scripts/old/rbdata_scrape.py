#!/usr/bin/python
import lxml.etree as ET
import urllib
import time
from dateutil.parser import parse
import datetime
from doppelserver.models import StaticSample, Sensor, SensorGroup, load_session
from doppelserver.utils import lookup_sensor, try_add
from doppelserver.log import logging_setup
import logging
from sqlalchemy.exc import IntegrityError

last_updated = {}
sensor_ids = {}

logging_setup("scrapers")
logger = logging.getLogger("redboard")
logger.warning("Starting redboard scraper")
slogger = logging.getLogger("sqlalchemy.engine")
#slogger.setLevel(logging.INFO)

def get_sensor_id(s, hostname, type):
    if sensor_ids.has_key((hostname, type)):
        sensor_id = sensor_ids[(hostname, type)]
    else:
        sensor = lookup_sensor(s, name=hostname, type=type)
        if sensor is not None:
            sensor_id = sensor.id
            sensor_ids[(hostname, type)] = sensor_id
        else:
            logger.debug("No sensor associated with %s (%s)", hostname, type)
            return None
    return sensor_id

def parse_data(s, xml):
    samples = []
    for node in xml:
        hostname = node.find("hostname").text
        if node.find("invalid-data") is not None: continue
        loc = node.find("location")
        building = loc.find("building").text
        floor = loc.find("floor").text
        if floor: floor = int(floor)
        room = loc.find("room").text
        timestamp = parse(node.find("time").text)

        if last_updated.has_key(hostname) and (timestamp - last_updated[hostname]).seconds < 1:
            continue
        last_updated[hostname] = timestamp

        for data in node:
            if data.text is None: continue
            if data.tag not in ["temperature", "humidity", "motion", "illuminance", "audio_level"]: continue
            sensor_id = get_sensor_id(s, hostname, data.tag)
            if sensor_id is None: continue
            samples.append(StaticSample(time=timestamp, data=float(data.text), sensor_id=sensor_id))

    return samples
if __name__ == "__main__":
    s = load_session()
    s.autoflush = False
    while True:
        try:
            f = urllib.urlopen("http://sensors.media.mit.edu/rb/alldata.fcgi")
            xml = ET.XML(f.read())
            f.close()
            samples = parse_data(s, xml)
            logger.info("Inserting %d new rows", len(samples))
            try:
                s.add_all(samples)
                s.commit()
            except IntegrityError:
                logger.warning("Insert failed due to duplicate time, retrying one-by-one")
                s.rollback()
                for sample in samples:
                    try:
                        s.add(sample)
                        s.commit()
                    except IntegrityError:
                        logger.debug("Duplicate entry for %s at %s", sample.sensor_id, str(sample.time))
                        s.rollback()
        except IOError:
            print "failed to get data at time %s" % time.strftime("%a, %d %b %Y %H:%M:%S")
        time.sleep(2)
