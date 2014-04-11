#!/usr/bin/env python

from __future__ import print_function

from gevent.monkey import patch_time
patch_time()

from flask import Flask
from flask_sockets import Sockets
from geventwebsocket import WebSocketError
from time import sleep

app = Flask(__name__)
sockets = Sockets(app)


@sockets.route('/data')
def data_socket(ws):
    data = 0
    while True:
        try:
            ws.send('Some Data: %d' % data)
        except WebSocketError as e:
            print('Caught WebSocketError: %s' % e)
            break
        sleep(2)
        data += 1
