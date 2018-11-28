from time import sleep

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
    sleep(1)    # It takes a time for subscribers to propagate to the publisher.
                # Without this sleep the first packages may be lost

    logger.info('Bound socket on {}'.format(port_pub))
    while True:
        if not queue.empty():
            data = queue.get()  # Should be a dictionary {'topic': topic, 'data': data}
            if 'stop_pub' in data:
                logger.debug('Stopping the publisher')
                socket.close()
                break
            logger.debug('Sending {} on {}'.format(data['data'], data['topic']))
            socket.send_string(data['topic'], zmq.SNDMORE)
            socket.send_pyobj(data['data'])
    sleep(1)  # Gives enough time to the subscribers to update their status
    logger.info('Stopped the publisher')

