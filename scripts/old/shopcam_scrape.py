#!/usr/bin/python

import urllib3, base64
from urlparse import urlsplit
from doppelserver.models import load_session, Image, ImageMinute, Sensor, SensorGroup
from time import sleep, time
from threading import Thread, Event
from signal import signal, pause, SIGTERM, SIGINT
import sys
from PIL import Image as PILImage, ImageChops as PILImageChops
from StringIO import StringIO
from datetime import datetime, timedelta

class ImageScraper(Thread):
   
    threshold = [0] * 20 + [255] * (256-20)

    def __init__(self, url, name, user=None, passwd=None):
        Thread.__init__(self)
        self.session = load_session()
        self.should_stop = Event()
        self.url = url
        self.path = urlsplit(url).path

        headers = {}
        if user is not None:
            if passwd is None: passwd = ""
            headers['Authorization'] = "Basic " + base64.encodestring("%s:%s" % (user, passwd))[:-1]

        self.http_pool = urllib3.connection_from_url(self.url, headers=headers)

        self.composite = None
        self.composite_bg = None
        self.composite_start = time()

        s = self.session
        q = s.query(SensorGroup).filter_by(name=name)
        if(q.count() != 1):
            raise SensorNotFoundError("Invalid sensor group name")
        self.group = q[0]
        q = s.query(Sensor).filter_by(group=self.group)
        if(q.count < 1):
            raise SensorNotFoundError("Sensor group contains no image sensors")
        self.sensor = q[0]

    def stop(self):
        self.should_stop.set()

    def fetch_image(self):
        try:    
            resp = self.http_pool.get_url(self.path)
        except Exception,e:
            print "Error fetching %s (%s)" % (self.url, repr(e))
            return None
        if resp.status != 200:
            print "Error fetching %s (HTTP error %d)" % (self.url, resp.status)
            return None

        try:
            framef = StringIO(resp.data)
            frame = PILImage.open(framef)
            frame.load()
            framef.close()
        except Exception, e:
            print "Error decoding image: %s" % repr(e)
            return resp.headers.get("Content-Type"), resp.data

        if self.composite is None:
            self.composite_bg = frame
            self.composite = frame
            self.composite_start = time()
        else:
            diff = PILImageChops.difference(self.composite_bg, frame)
            diff = diff.convert("L")
            #diff = diff.point(self.threshold)
            #print diff.mode
            self.composite = PILImageChops.composite(self.composite, frame, diff)
            #self.composite = PILImage.blend(self.composite, frame, 0.5)
            #self.composite = PILImageChops.multiply(self.composite, frame)

        #print self.url
        return resp.headers.get("content-type"), resp.data

    def update_db(self):
        im = self.fetch_image()
        if im is None:
            return
        mimetype, data = im

        image = Image(sensor=self.sensor, mimetype=mimetype, data=data)
        self.session.add(image)

        if time() - self.composite_start > 60.0 and self.composite is not None:
            compositef = StringIO()
            self.composite.save(compositef, "JPEG", quality=40, optimize=True)
            composite_data = compositef.getvalue()
            compositef.close()
            image_minute = ImageMinute(sensor=self.sensor, mimetype="image/jpeg", 
                data=composite_data)
            self.session.add(image_minute)
            self.composite = None
            print "Saved composite"

        self.session.commit()

    def run(self):
        while not self.should_stop.isSet():
            lasttime = time()
            self.update_db()
            trem = 5.0 - (time() - lasttime) 
            if trem < 0.0: trem = 0.0
            #print self.url, trem
            sleep(trem)

class DatabaseCleaner(Thread):
    
    def __init__(self, td):
        Thread.__init__(self)
        self.td = td
        self.should_stop = Event()
        self.session = load_session()
        self.last_ran = 0

    def stop(self):
        self.should_stop.set()
        
    def run(self):    
        while not self.should_stop.is_set():
            if time() - self.last_ran > 600:
                mintime = datetime.now() - self.td
                print "Deleting records older than %s" % str(mintime)
                self.session.query(Image).filter(Image.time < mintime).delete()
                self.session.commit()
                self.last_ran = time()
            sleep(1)
        
            

class SensorNotFoundError(Exception):
    pass

if __name__ == '__main__':
    s = load_session()

    scrapers = [
        #ImageScraper('http://localhost:3333/cgi/jpg/image.cgi', 'cam_lasercutter', 'fab'),
        ImageScraper('http://18.85.8.109/cgi/jpg/image.cgi', 'cam_lasercutter', 'fab'),
        ImageScraper('http://18.85.8.110/cgi/jpg/image.cgi', 'cam_3dprinters', 'fab'),
        ImageScraper('http://18.85.8.111/cgi/jpg/image.cgi', 'cam_bandsaw', 'fab'),
        ImageScraper('http://18.85.8.112/cgi/jpg/image.cgi', 'cam_waterjet', 'fab'),
        ImageScraper('http://18.85.8.113/cgi/jpg/image.cgi', 'cam_shopbot', 'fab'),
        ImageScraper('http://18.85.8.114/cgi/jpg/image.cgi', 'cam_hurco', 'fab'),
        ImageScraper('http://18.85.8.115/cgi/jpg/image.cgi', 'cam_lathe', 'fab'),
        ImageScraper('http://foodcam.media.mit.edu/axis-cgi/jpg/image.cgi', 'cam_foodcam'),
        DatabaseCleaner(timedelta(hours=24)),
    ]

    def shutdown(signum, frame):
        print "Caught signal %d, shutting down" % signum
        for scraper in scrapers:
            scraper.stop()
            #scraper.join()
        sys.exit(0)


    signal(SIGTERM, shutdown)
    signal(SIGINT, shutdown)

    for scraper in scrapers:
        scraper.start()

    pause()
