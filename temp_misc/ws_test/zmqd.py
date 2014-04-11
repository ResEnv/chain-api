#!/usr/bin/env python

from __future__ import print_function
import zmq
from time import sleep

zmq_ctx = zmq.Context()
zmq_sock = zmq_ctx.socket(zmq.PUB)
zmq_sock.bind('tcp://127.0.0.1:31416')

datanum = 0
while True:
    data = 'data %d' % datanum
    print('Publishing "%s"' % data)
    zmq_sock.send(data)
    datanum += 1
    sleep(1)
