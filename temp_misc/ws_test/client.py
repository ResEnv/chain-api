#!/usr/bin/env python

from websocket import create_connection
import sys

ws = create_connection("ws://localhost:8000/sites/%s" % sys.argv[1])
while True:
    result = ws.recv()
    print "Received '%s'" % result
ws.close()
