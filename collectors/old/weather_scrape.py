#!/usr/bin/python
"""Scrape data from Google's weather API."""

from doppelserver.models import Sensor, SensorGroup, StaticSample, load_session
from sqlalchemy.exc import IntegrityError

from lxml import etree

from dateutil import parser, tz
import urllib
import re

session = load_session()
weather_query = session.query(Sensor).join(SensorGroup).filter(
    SensorGroup.name =="cambridge google weather")
temperature_sensor = weather_query.filter(Sensor.type == "temperature").first()
humidity_sensor = weather_query.filter(Sensor.type == "humidity").first()

def parse_xml(xml):
    weather_base = xml.xpath('/xml_api_reply/weather')[0]
    time_string = weather_base.xpath('forecast_information/current_date_time/@data')[0]
    time = parser.parse(time_string).astimezone(tz.gettz('America/New_York'))
    temperature = int(weather_base.xpath('current_conditions/temp_c/@data')[0])
    humidity_string = weather_base.xpath('current_conditions/humidity/@data')[0]
    humidity = int(re.findall("(\d+)", humidity_string)[0])
    return time, temperature, humidity

if __name__ == "__main__":
    try:
        f = urllib.urlopen("http://www.google.com/ig/api?weather=Cambridge,%20MA")
        xml = etree.XML(f.read())
        f.close()
        time, temperature, humidity = parse_xml(xml)
        
        session.add_all([
            StaticSample(time=time, sensor=temperature_sensor, data=temperature),
            StaticSample(time=time, sensor=humidity_sensor, data=humidity)
            ])
    except IOError, e:
        print "failed at %s, %s" % (time.strftime("%a, %d %b %Y %H:%M:%S"), e)
    except IntegrityError: # happens when we get the same time point twice
        session.rollback()
