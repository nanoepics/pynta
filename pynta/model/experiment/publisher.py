import zmq

from pynta.util.log import get_logger


def publisher(queue, port=5555):
    """ Simple method that starts a publisher on the port 5555.

    .. TODO:: The publisher's port should be determined in a configuration file.
    """
    logger = get_logger(name=__name__)
    port_pub = port
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % port_pub)
    logger.info('Bound socket on {}'.format(port_pub))
    # sleep(1)
    while True:
        if not queue.empty():
            data = queue.get()  # Should be a dictionary {'topic': topic, 'data': data}
            logger.debug('Sending {} on {}'.format(data['data'], data['topic']))
            socket.send_string(data['topic'], zmq.SNDMORE)
            socket.send_pyobj(data['data'])
            if 'stop_pub' in data:
                break
    logger.info('Stopping publisher')

