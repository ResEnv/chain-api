#!/usr/bin/python
import urllib, csv
from time import sleep
from doppelserver.models import *
from doppelserver.utils import lookup_sensor, try_add
from doppelserver.log import logging_setup
import logging
from dateutil.parser import parse
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

atriumUrl = "http://18.85.58.52/SensorDataWebInterface/SensorDescriptionText.aspx?database=Phase3a"

logging_setup("scrapers")
logger = logging.getLogger("atrium")
logger.warning("Starting atrium scraper")
slogger = logging.getLogger("sqlalchemy.engine")
#slogger.setLevel(logging.INFO)

last_updated = {}
sensor_ids = {}

def get_sensor_id(s, mac, type):
    if sensor_ids.has_key((mac, type)):
        sensor_id = sensor_ids[(mac, type)]
    else:
        sensor = lookup_sensor(s, name=mac, type=type)
        if sensor is not None:
            sensor_id = sensor.id
            sensor_ids[(mac, type)] = sensor_id
        else:
            logger.debug("No sensor associated with %s (%s)", mac, type)
            #print "NONE SENSOR", (mac, type)
            return None
    return sensor_id

if __name__ == "__main__":
    s = load_session()
    while True:
        try:
            unchanged_rows = 0
            changed_rows = 0
            new_rows = []
            failed = False

            atriumReader = csv.reader(urllib.urlopen(atriumUrl))
            for row in atriumReader:
                mac, __, __, time, temp, humidity = row
                try:
                    time = parse(time)
                except ValueError:
                    continue
                if not ":" in mac:
                    continue
                if last_updated.has_key(mac) and (time - last_updated[mac]).seconds < 1:
                    unchanged_rows += 1
                    continue
                changed_rows += 1
                now = datetime.now()
                last_updated[mac] = time
                try:
                    sensor_id_t = get_sensor_id(s, mac, "temperature")
                    sensor_id_h = get_sensor_id(s, mac, "humidity")

                    if temp != " " and float(temp) and ":" in mac and sensor_id_t is not None:
                        new_rows.append(StaticSample(time, data=float(temp), sensor_id=sensor_id_t))
                    if humidity != " " and float(humidity) and sensor_id_h is not None:
                        new_rows.append(StaticSample(time, data=float(humidity), sensor_id=sensor_id_h))
                except IntegrityError:
                    s.rollback()
                    logger.debug("rollback")
        except IOError, e:
            print "failed to get data at time %s, %s" % (time.strftime("%a, %d %b %Y %H:%M:%S"), e)
            failed = True
        
        if not failed:
            logger.info("Inserting %d new samples and ignoring %d unchanged samples",
                changed_rows, unchanged_rows)
            try:
                s.add_all(new_rows)
                s.commit()
            except IntegrityError:
                logger.warning("Insert failed due to duplicate time, retrying one-by-one")
                s.rollback()
                failed = True
            if failed:
                for row in new_rows:
                    try:
                        s.add(row)
                        s.commit()
                    except IntegrityError:
                        s.rollback()
                        logger.debug("Duplicate entry for %d at %s", row.sensor_id, str(row.time))
                        
        sleep(30)
