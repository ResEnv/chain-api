from websocket import create_connection
import time
import Queue
import threading
import urllib2

def make_connection(tc, url, connection):
    print "Connection %5d" % connection
    ws = create_connection(url)
    time.sleep(0.2)
    print "  Connected %5d. Waiting..." % connection
    ws.close()
    # print "  Closed %5d." % connection
    tc.available_threads += 1

class ThreadTracker:
    def __init__(self, avail_threads, url):
        self.available_threads = avail_threads
        self.url = url

    def get_thread(self, inputs):
        for input_val in inputs:
            while self.available_threads == 0:
                time.sleep(0.5)
            self.available_threads -= 1
            yield threading.Thread(target=make_connection, args = (self, self.url, input_val))

def run_volume_test(url, total_connections=10000, concurrent_connections=64):
    theconnections = xrange(total_connections)
    tc = ThreadTracker(concurrent_connections, url)

    for t in tc.get_thread(theconnections):
        t.daemon = True
        t.start()

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--total-connections", help="Total number of connections to make to server", type=int, default=10000)
parser.add_argument("-c", "--concurrent-connections", help="Number of concurrent connections to make to server", type=int, default=200)
parser.add_argument("url", help="websocket url ws://localhost:8080/ws/site-1, for example")
args = parser.parse_args()
run_volume_test(args.url, total_connections=args.total_connections or 10000, concurrent_connections=args.concurrent_connections or 200)
