# run with
#   gunicorn -k flask_sockets.worker chain.websocketd:app
# make sure you've run setup.py to install flask_sockets

from __future__ import print_function

import zmq.green as zmq
import gevent
from flask import Flask
from flask_sockets import Sockets
from zmq_passthrough import passthrough
from chain.settings import ZMQ_PASSTHROUGH_URL_PUB
import logging
import coloredlogs

app = Flask(__name__)
app.debug = False
zmq_ctx = zmq.Context()
websockets = Sockets(app)

coloredlogs.install(logging.INFO)
logger = logging.getLogger(__name__)

logger.info("websocketd.py started")


@websockets.route('/<tag>')
def site_socket(ws, tag):
    logger.info('ws client connected for tag "%s"' % tag)
    zmq_sock = zmq_ctx.socket(zmq.SUB)
    zmq_sock.connect(ZMQ_PASSTHROUGH_URL_PUB)
    # note that flask gives us tag as a unicode string
    zmq_sock.setsockopt_string(zmq.SUBSCRIBE, tag)
    while True:
        in_data = zmq_sock.recv()
        # in case we later subscribe to multiple topic, get the topic from the
        # incoming message
        msg_tag, _, msg = in_data.partition(' ')
        logger.debug('Received on tag "%s": %s' % (msg_tag, msg))
        try:
            ws.send(msg)
        except Exception as e:
            logger.info('Caught Error sending to client: %s' % e)
            break
    logger.info('Disconnecting ZMQ Socket for tag "%s"' % tag)
    zmq_sock.disconnect(ZMQ_PASSTHROUGH_URL_PUB)
    # return an empty response so Flask doesn't complain
    return ''

# Start the passthrough process:
gevent.spawn(passthrough, zmq_context=zmq_ctx)
