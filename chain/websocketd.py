# run with
#   gunicorn -k flask_sockets.worker zmq-ws:app
# make sure you've run setup.py to install flask_sockets

from __future__ import print_function

import zmq.green as zmq
from flask import Flask
from flask_sockets import Sockets
from geventwebsocket import WebSocketError
from chain.settings import ZMQ_PUB_URL

app = Flask(__name__)
app.debug = True
zmq_ctx = zmq.Context()
websockets = Sockets(app)


@websockets.route('/<tag>')
def site_socket(ws, tag):
    print('ws client connected for tag "%s"' % tag)
    zmq_sock = zmq_ctx.socket(zmq.SUB)
    zmq_sock.connect(ZMQ_PUB_URL)
    # note that flask gives us tag as a unicode string
    zmq_sock.setsockopt_string(zmq.SUBSCRIBE, tag)
    while True:
        in_data = zmq_sock.recv()
        # in case we later subscribe to multiple topic, get the topic from the
        # incoming message
        msg_tag, _, msg = in_data.partition(' ')
        print('Received on tag "%s": %s' % (msg_tag, msg))
        try:
            ws.send(msg)
        except WebSocketError as e:
            print('Caught WebSocketError: %s' % e)
            break
    zmq_sock.disconnect(ZMQ_PUB_URL)
