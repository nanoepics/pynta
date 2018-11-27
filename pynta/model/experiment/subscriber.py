"""
    subscriber.py
    =============
    Example script on how to run separate processes to process the data coming from a publisher like the one on
    ``publisher.py``. The first process just grabs the frame and puts it in a Queue. The Queue is then used by
    another process in order to analyse, process, save, etc. It has to be noted that on UNIX systems, getting
    from a queue with ``Queue.get()`` is particularly slow, much slower than serializing a numpy array with
    cPickle.
"""
import zmq
from pynta.util import get_logger


def subscriber(func, topic, *args, **kwargs):
    port = 5555
    if 'port' in kwargs:
        port = kwargs['port']
    logger = get_logger(name=__name__)
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:%s" % port)

    topic_filter = topic.encode('ascii')
    socket.setsockopt(zmq.SUBSCRIBE, topic_filter)
    logger.info('Subscribing {} to {}'.format(func.__name__, topic))
    while True:
        topic = socket.recv_string()
        data = socket.recv_pyobj()  # flags=0, copy=True, track=False)
        logger.debug('Got data of type {} on topic: {}'.format(type(data), topic))
        if isinstance(data, str):
            logger.debug('Data: {}'.format(data))
            if data == 'stop':
                logger.info('Stopping subscriber on method {}'.format(func.__name__))
                break
        func(data, *args, **kwargs)
    logger.debug('Stopped subscriber {}'.format(func.__name__))
