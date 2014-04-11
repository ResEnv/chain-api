#!/usr/bin/python

import urllib
import time
from datetime import datetime
from doppelserver.models import Event, load_session
from sqlalchemy.sql import func
from lxml import etree
import doppelserver.utils as utils

def hit_to_event(hit_xml, sensor=None):
    # the table is a 1280x768 sensor
    # we scale by that so that changing the sensor
    # resolution doesn't invalidate all our old data

    position = hit_xml.xpath("position")[0]
    json = dict(position.attrib)

    time = hit_xml.xpath("time")[0]
    time_data = dict([(k, int(v)) for (k, v) in time.attrib.items()])
    # remove ms since we don't care about milliseconds and it's not a
    # valid keyword argument to datetime anyway
    # deal with AM/PM
    if time_data["PM"] == 1:
        time_data["hour"] += 12
    del time_data["PM"]

    json["ms"] = time_data["ms"]
    del time_data["ms"]
    dt = datetime(**time_data)

    return Event(sensor=sensor, time=dt, json=json)
    
    
if __name__ == "__main__":
    s = load_session()
    s.autoflush = False
    sensor = utils.lookup_sensor(s, "Ping pong table", "ping_pong")

    while True:
        # last_time is the most recent ping pong update
        last_event = s.query(Event).filter_by(sensor=sensor).order_by(Event.time.desc()).first()

        xml = etree.XML(urllib.urlopen("http://18.111.48.39/~tmg/pppp/hits.txt").read())
        for hit in xml:
            event = hit_to_event(hit, sensor=sensor)
            # don't add stuff that's older than the last update
            if event.time <= last_event.time:
                s.expunge(event)

        s.commit()
        time.sleep(1)
