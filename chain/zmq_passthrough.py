import zmq
from chain.settings import ZMQ_PASSTHROUGH_URL_PULL, \
    ZMQ_PASSTHROUGH_URL_PUB

zmq_ctx = zmq.Context()


def passthrough():
    zmq_sock_pull = zmq_ctx.socket(zmq.PULL)
    zmq_sock_pull.bind(ZMQ_PASSTHROUGH_URL_PULL)

    zmq_sock_pub = zmq_ctx.socket(zmq.PUB)
    zmq_sock_pub.bind(ZMQ_PASSTHROUGH_URL_PUB)
    while True:
        zmq_sock_pub.send_string(zmq_sock_pull.recv())

# If being run as a seperate process:
if __name__ == '__main__':
    passthrough()
