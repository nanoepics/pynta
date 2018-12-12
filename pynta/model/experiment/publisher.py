# -*- coding: utf-8 -*-
"""
    publisher.py
    ~~~~~~~~~~~~
    Publishers are responsible for broadcasting the message over the ZMQ PUB/SUB architecture.

    .. TODO:: In the current implementation, data is serialized for being added to a Queue, then deserialized by the
    publisher and serialized again to be sent. These three steps could be simplify into one if, for example, one assumes
    that objects where pickled. There is also a possibility of assuming numpy arrays and using a zero-copy strategy.

    :copyright:  Aquiles Carattino <aquiles@aquicarattino.com>
    :license: GPLv3, see LICENSE for more details
"""

import logging
from multiprocessing import Queue, Event, Process
from time import sleep
import zmq

from pynta import general_stop_event
from pynta.util.log import get_logger


class Publisher:
    """ Publisher class in which the queue for publishing messages is defined and also a separated process is started.
    It is important to have a new process, since the serialization/deserialization of messages from the QUEUE may be
    a bottleneck for performance.
    """
    def __init__(self, port=5555):
        self.logger = get_logger(name=__name__)
        self._port = port
        self._queue = Queue()  # The publisher will grab and broadcast the messages from this queue
        self._event = Event()   # This event is used to stop the process
        self._process = Process(target=publisher, args=[self._queue, self._event, self._port])
        self.logger.info('Initialized published on port {}'.format(port))

    def start(self):
        """ Start a new process that will be responsible for broadcasting the messages.
        """
        self._event.clear()
        self._process.start()
        sleep(1)  # This forces the start to block until the publisher is ready

    def stop(self):
        self._event.set()
        self.empty_queue()

    def empty_queue(self):
        """ If the publisher stops before broadcasting all the messages, the Queue may still be using some memory. This
        method is simply getting all the elements in order to free memory. Can be useful for garbage collection or
        better control of the downstream program.
        """
        self.logger.info('Emptying the queue of the publisher')
        self.logger.debug('Queue length: {}'.format(self._queue.qsize()))
        self._queue.close()

    def publish(self, topic, data):
        """ Adapts the data to make it faster to broadcast

        :param str topic: Topic in which to publish the data
        :param data: Data to be published
        :return: None
        """
        self.logger.debug('Adding data of type {} to topic {}'.format(type(data), topic))
        try:
            self._queue.put({'topic': topic, 'data': data})
        except AssertionError:
            # This means the queue has been closed already
            pass

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, new_port):
        if new_port != self._port:
            self._port = new_port
            self.logger.warning('Changing the port requires restarting the publisher process')
            self.logger.debug('Setting the new publisher port to {}'.format(new_port))
            self.stop()
            self._process.join()
            self._process = Process(target=publisher, args=[self._queue, self._event, self._port])
            self.start()
        else:
            self.logger.warning('New port {} is the same as the old port'.format(new_port))

    def join(self, timeout=0):
        if self._process.is_alive():
            self.logger.debug('Waiting for Publisher process to finish')
            self._process.join(timeout)


def publisher(queue, event, port):
    """ Simple method that starts a publisher on the port 5555.

    :param multiprocessing.Queue queue: Queue of messages to be broadcasted
    :param multiprocessing.Event event: Event to stop the publisher
    :param int port: port in which to broadcast data
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
    while not event.is_set():
        while not queue.empty():
            data = queue.get()  # Should be a dictionary {'topic': topic, 'data': data}
            logger.debug('Sending {} on {}'.format(data['data'], data['topic']))
            socket.send_string(data['topic'], zmq.SNDMORE)
            socket.send_pyobj(data['data'])
            if general_stop_event.is_set():
                break
        sleep(0.05)  # Sleeps 5 milliseconds to be polite with the CPU

    sleep(1)  # Gives enough time to the subscribers to update their status
    socket.close()
    logger.info('Stopped the publisher')


if __name__ == "__main__":
    logger = get_logger(name=__name__)  # 'pynta.model.experiment.nano_cet.saver'
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    p = Publisher()
    p.start()
    p.publish('Testing', [1, 2, 3, 4])
    sleep(1)
    p.stop()
    p.join()