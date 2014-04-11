#!/usr/bin/env python

from websocket import create_connection
import sys

try:
    tag = sys.argv[1]
except IndexError:
    print('usage: %s <STREAM_URL>' % sys.argv[0])
    sys.exit(1)

stream_url = sys.argv[1]
print('Connecting to %s' % stream_url)
ws = create_connection(stream_url)
while True:
    result = ws.recv()
    print "Received '%s'" % result

ws.close()
