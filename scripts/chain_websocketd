#!/usr/bin/env python

from __future__ import print_function

import zmq.green as zmq
from flask import Flask
from flask_sockets import Sockets
from geventwebsocket import WebSocketError

zmq_ctx = zmq.Context()
app = Flask(__name__)
websockets = Sockets(app)

ZMQ_ADDR = 'tcp://127.0.0.1:31416'


@websockets.route('/sites/<int:site_id>')
def data_socket(ws, site_id):
    print('ws client connected for site %d' % site_id)
    zmq_sock = zmq_ctx.socket(zmq.SUB)
    zmq_sock.connect(ZMQ_ADDR)
    # subscribe to all topics
    zmq_sock.setsockopt(zmq.SUBSCRIBE, "")
    while True:
        in_data = zmq_sock.recv()
        print('Received from zmq: %s' % in_data)
        try:
            ws.send(in_data)
        except WebSocketError as e:
            print('Caught WebSocketError: %s' % e)
            break
    zmq_sock.disconnect(ZMQ_ADDR)
