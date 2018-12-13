"""
    subscriber.py
    =============
    Example script on how to run separate processes to process the data coming from a publisher like the one on
    ``publisher.py``. The first process just grabs the frame and puts it in a Queue. The Queue is then used by
    another process in order to analyse, process, save, etc. It has to be noted that on UNIX systems, getting
    from a queue with ``Queue.get()`` is particularly slow, much slower than serializing a numpy array with
    cPickle.
"""
from time import sleep

import zmq
from pynta.util import get_logger


def subscribe(port, topic):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:%s" % port)
    sleep(1)  # Takes a while for TCP connections to propagate
    topic_filter = topic.encode('ascii')
    socket.setsockopt(zmq.SUBSCRIBE, topic_filter)
    return socket


def subscriber(func, topic, event, *args, **kwargs):
    port = 5555
    if 'port' in kwargs:
        port = kwargs['port']
        del kwargs['port']

    logger = get_logger(name=__name__)
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:%s" % port)
    sleep(1)  # Takes a while for TCP connections to propagate
    topic_filter = topic.encode('ascii')
    socket.setsockopt(zmq.SUBSCRIBE, topic_filter)
    logger.info('Subscribing {} to {}'.format(func.__name__, topic))
    while not event.is_set():
        topic = socket.recv_string()
        data = socket.recv_pyobj()  # flags=0, copy=True, track=False)
        logger.debug('Got data of type {} on topic: {}'.format(type(data), topic))
        if isinstance(data, str):
            logger.debug('Data: {}'.format(data))
            if data == 'stop':
                logger.debug('Stopping subscriber on method {}'.format(func.__name__))
                break

        func(data, *args, **kwargs)
    sleep(1)  # Gives enough time for the publishers to finish sending data before closing the socket
    socket.close()
    logger.debug('Stopped subscriber {}'.format(func.__name__))
