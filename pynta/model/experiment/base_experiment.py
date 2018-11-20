# -*- coding: utf-8 -*-
"""
    base_experiment.py
    ~~~~~~~~~~~~~~~~~~
    Base class for the experiments. ``BaseExperiment`` defines the common patterns that every experiment should have.
    Importantly, it starts an independent process called publisher, that will be responsible for broadcasting messages
    that are appended to a queue. The messages rely on the pyZMQ library and should be tested further in order to
    assess their limitations. The general pattern is that of the PUB/SUB, with one publisher and several subscribers.

    The messages should include a *topic* and data. For this, the elements in the queue should be dictionaries with two
    keywords: **data** and **topic**. ``data['data']`` will be serialized through the use of cPickle, and is handled
    automatically by pyZQM through the use of ``send_pyobj``. The subscribers should be aware of this and use either
    unpickle or ``recv_pyobj``.

    In order to stop the publisher process, the string ``'stop'`` should be placed in ``data['data']``. The message
    will be broadcast and can be used to stop other processes, such as subscribers.

    .. TODO:: Check whether the serialization of objects with cPickle may be a bottleneck for performance.


    :copyright:  Aquiles Carattino <aquiles@aquicarattino.com>
    :license: GPLv3, see LICENSE for more details
"""
from multiprocessing import Queue, Process
from time import sleep

import numpy as np
import zmq
import yaml
from threading import Thread

from pynta.util import get_logger


class BaseExperiment:
    """ Base class to define experiments. Should keep track of the basic methods needed regardless of the experiment
    to be performed. For instance, a way to start and a way to finalize a measurement.
    """
    def __init__(self):
        self.config = {}  # Dictionary storing the configuration of the experiment
        self.logger = get_logger(name=__name__)
        self.async_threads = []
        self.queue = Queue()
        self._publisher = Process(target=self.start_publisher)
        self._publisher.start()

        self._connections = []

    def start_publisher(self):
        """ Simple method that starts a publisher on the port 5555.

        .. TODO:: The publisher's port should be determined in a configuration file.
        """

        port_pub = 5555
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.bind("tcp://*:%s" % port_pub)
        sleep(1)
        while True:
            if not self.queue.empty():
                data = self.queue.get()  # Should be a dictionary {'topic': topic, 'data': data}
                logger.debug('Sending {} on {}'.format(data['data'], data['topic']))
                socket.send_string(data['topic'], zmq.SNDMORE)
                socket.send_pyobj(data['data'])
                if 'stop_pub' in data:
                    break

    def stop_publisher(self):
        """ Puts the proper data to the queue in order to stop the running publisher process"""
        self.stop_subscribers()
        self.queue.put({'stop_pub': True, 'topic': '', 'data': 'stop_pub'})

    def stop_subscribers(self):
        for connection in self._connections:
            if connection['process'].is_alive():
                logger.info('Stopping {}'.format(connection['method']))
                self.queue.put({'topic': connection['topic'], 'data': 'stop'})


    def connect(self, method, topic):
        """ Async method that connects the running publisher to the given method on a specific topic.
        """
        def subscriber(method=method, topic=topic, port=5555):
            port = port

            context = zmq.Context()
            socket = context.socket(zmq.SUB)
            socket.connect("tcp://localhost:%s" % port)

            topic_filter = topic.encode('ascii')
            socket.setsockopt(zmq.SUBSCRIBE, topic_filter)
            sleep(1)
            self.logger.info('Subscribing {} to {}'.format(method.__name__, topic))
            while True:
                topic = socket.recv_string()
                img = socket.recv_pyobj()  # flags=0, copy=True, track=False)
                logger.debug('Got data of type {} on topic: {}'.format(type(img), topic))
                method(img)
                if isinstance(img, str):
                    self.logger.debug('Data: {}'.format(img))
                    if img == 'stop':
                        self.logger.info('Stopping subscriber on method {}'.format(method.__name__))
                        break

        self._connections.append({
            'method':method.__name__,
            'topic': topic,
            'process': Process(target=subscriber),
        })
        self._connections[-1]['process'].start()

    def print_me(self, me):
        print('me')

    def also_print_me(self, also_me):
        print('Also me')

    def load_configuration(self, filename):
        """ Loads the configuration file in YAML format.

        :param str filename: full path to where the configuration file is located.
        :raises FileNotFoundError: if the file does not exist.
        """
        try:
            with open(filename, 'r') as f:
                self.config = yaml.load(f)
        except FileNotFoundError:
            self.logger.error('The specified file {} could not be found'.format(filename))
            raise
        except Exception as e:
            self.logger.exception('Unhandled exception')
            raise

    def make_async(self, func, *args, **kwargs):
        """ Wrapper function for making any function async. It will create a new thread, not a new process.
        Threads are less delicate and allow to share memory more easily than processes. Every new thread will be
        stored in a list. This enables the user to trigger more than one thread, for instance for saving data while
        acquiring, or while analysing, etc.

        .. note:: It is not a different process, but a thread spawn from the main thread.
        """
        self.logger.info('Starting a new thread for {}'.format(func.__name__))
        self.async_threads.append([func.__name__, Thread(target=func, args=args, kwargs=kwargs)])
        self.async_threads[-1][1].start()
        self.logger.debug('Started a new thread for {}'.format(func.__name__))
        self.logger.debug('In total, there are {} threads'.format(len(self.async_threads)))

    def clear_threads(self):
        """ Keep only the threads that are alive.
        """
        self.async_threads = [thread for thread in self.async_threads if thread[1].is_alive()]

    @property
    def num_threads(self):
        return len(self.async_threads)

    @property
    def connections(self):
        return self._connections

    @property
    def alive_threads(self):
        alive_threads = 0
        for thread in self.async_threads:
            if thread[1].is_alive():
                alive_threads += 1
        return alive_threads

    @property
    def list_alive_threads(self):
        alive_threads = []
        for thread in self.async_threads:
            if thread[1].is_alive():
                alive_threads.append(thread)
        return alive_threads

    def set_up(self):
        """ Needs to be overridden by child classes.
        """
        pass

    def finalize(self):
        """ Needs to be overridden by child classes.
        """
        pass

    def update_config(self, **kwargs):
        self.config.update(**kwargs)

    def __enter__(self):
        self.set_up()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.info("Exiting the experiment")
        self.finalize()
        self.stop_publisher()
        self._publisher.join(timeout=5)
        for conn in self.connections:
            self.logger.debug('Number of open connections: {}'.format(len(self.connections)))
            conn['process'].join()
        while not self.queue.empty():
            self.logger.debug('Queue size while exiting: {}'.format(self.queue.qsize()))
            self.queue.get()



if __name__ == '__main__':
    import logging

    logger = get_logger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    with BaseExperiment() as exp:
        sleep(2)
        exp.connect(exp.print_me, 'image')
        exp.connect(exp.also_print_me, 'nothing')

        exp.update_config(timelapse=2, framerate=4)

        data = {'topic': 'image', 'data': np.random.random((1,1))}
        for i in range(5):
            exp.queue.put(data)
            sleep(0.001)
        data.update({'topic': 'nothing'})
        for i in range(5):
            exp.queue.put(data)
            sleep(0.001)

    print('exit')