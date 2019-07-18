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

zmq_socks = set()
zmq_socks_tag = {}
tag_zmq_sock = {}
tag_subscribers = {}

@websockets.route('/<tag>')
def site_socket(ws, tag):
    logger.info('ws client connected for tag "%s"' % tag)
    if tag in tag_zmq_sock:
        tag_subscribers[tag].add(ws)
    else:
        zmq_sock = zmq_ctx.socket(zmq.SUB)
        zmq_sock.connect(ZMQ_PASSTHROUGH_URL_PUB)
        # note that flask gives us tag as a unicode string
        zmq_sock.setsockopt_string(zmq.SUBSCRIBE, tag)
        zmq_socks.add(zmq_sock)
        zmq_socks_tag[zmq_sock] = tag
        tag_zmq_sock[tag] = zmq_sock
        tag_subscribers[tag] = {ws}
    while True:
        try:
            # Read from ws socket continuously.
            # XXX:  This builds up a lot of threads.  Is there ANY way we could do
            #       this for many connected ws clients in a non-blocking fashion (like select).
            # NOTE that ws dies if site_socket function exits...
            received = ws.receive()
            logger.info("Received from ws client: %s" % received)
        except Exception as e:
            tag_subscribers[tag].remove(ws)
            if len(tag_subscribers) == 0:
                close_socket(tag_zmq_sock[tag])
            break
    # return an empty response so Flask doesn't complain
    return ''

def close_socket(zmq_sock):
    tag = zmq_socks_tag[zmq_sock]
    logger.info('Disconnecting ZMQ Socket for tag "%s"' % tag)
    try:
        zmq_sock.disconnect(ZMQ_PASSTHROUGH_URL_PUB)
    except Exception as e:
        logger.info(str(e))
    zmq_socks.remove(zmq_sock)
    del zmq_socks_tag[zmq_sock]
    del tag_zmq_sock[tag]
    subscribers = tag_subscribers[tag]
    del tag_subscribers[tag]
    for ws in tag_subscribers:
        try:
            ws.close()
        except Exception:
            logger.info('Could not close ws socket cleanly.')

def select_zmq_socks():
    logger.info("Starting select loop over ZMQ sockets")
    while True:
        while len(zmq_socks) == 0:
            gevent.sleep(seconds=0.0625, ref=True)
        # It's important to have a timeout for the select loop, because
        #   if more sockets are added, they won't be slected for until
        #   the next iteration of the while loop
        socks_list = list(zmq_socks)
        rlist, wlist, xlist = zmq.select(socks_list, [], socks_list, timeout=0.0625)
        for zmq_sock in xlist:
            tag = zmq_socks_tag[zmq_sock]
            logger.info('Error on ZMQ socket on tag "%s".' % tag)
            close_socket(zmq_sock)
        for zmq_sock in rlist:
            tag = zmq_socks_tag[zmq_sock]
            logger.info('Reading from socket on tag "%s".' % tag)
            msg_tag, _, msg = zmq_sock.recv().partition(" ")
            logger.info('Received on tag "%s": %s' % (msg_tag, msg))
            to_remove = set()
            for ws in tag_subscribers[tag]:
                try:
                    ws.send(msg)
                except Exception as e:
                    logger.info('Caught Error sending to client: %s' % e)
                    try:
                        ws.close()
                    except Exception:
                        logger.info('Could not close ws socket cleanly.')
                    to_remove.add(ws)
            tag_subscribers[tag].difference_update(to_remove)
            if len(tag_subscribers[tag]) == 0:
                close_socket(zmq_sock)

logger.info("Starting gevent processess...")
# Start the passthrough process:
gevent.spawn(passthrough, zmq_context=zmq_ctx)
# Start the zmq socket selection loop:
gevent.spawn(select_zmq_socks)
