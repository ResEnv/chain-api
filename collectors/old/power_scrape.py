#!/usr/bin/python

from doppelserver.models import load_session, StaticSample
import urllib, time
import doppelserver.utils as utils
from lxml import etree

if __name__ == "__main__":
    s = load_session()
    while True:
        f = urllib.urlopen("http://tac.mit.edu/E14/data.asp")
        xml = etree.XML(f.read())
        f.close()
        power = int(xml.xpath("string()").strip())
        sensor = utils.lookup_sensor(s, "Building power usage", "power")
        sample = StaticSample(time=None, data=power, sensor=sensor)
        s.add(sample)
        s.commit()
        time.sleep(45)
