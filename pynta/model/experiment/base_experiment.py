# -*- coding: utf-8 -*-
"""
    base_experiment.py
    ==================
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


    :copyright:  Aquiles Carattino <aquiles@uetke.com>
    :license: GPLv3, see LICENSE for more details
"""
from multiprocessing import Process, Event

import yaml
import importlib

from pynta.util import get_logger
from pynta.model.experiment.publisher import Publisher
from pynta.model.experiment.subscriber import subscriber


class BaseExperiment:
    """ Base class to define experiments. Should keep track of the basic methods needed regardless of the experiment
    to be performed. For instance, a way to start and a way to finalize a measurement.
    """
    def __init__(self, filename=None):
        self.config = {}  # Dictionary storing the configuration of the experiment
        self.logger = get_logger(name=__name__)
        self._threads = []
        self.publisher = Publisher()
        self.publisher.start()

        self._connections = []
        self.subscriber_events = []
        if filename:
            self.load_configuration(filename)
        self.initialize_camera()
    
    """which folder view to use for the GUI. Let's differen experiments use different files.
    """
    def gui_file(self):
        return None
    
    def initialize_camera(self):
        print("init cam!!!")
        """ Initializes the camera to be used to acquire data. The information on the camera should be provided in the
        configuration file and loaded with :meth:`~self.load_configuration`. It will load the camera assuming
        it is located in nanoparticle_tracking/model/cameras/[model].

        .. TODO:: Define how to load models from outside of PyNTA. E.g. from a user-specified folder.
        """
        # try:
        #     self.logger.info('Importing camera model {}'.format(self.config['camera']['model']))
        #     self.logger.debug('pynta.model.cameras.' + self.config['camera']['model'])

        #     camera_model_to_import = 'pynta.model.cameras.' + self.config['camera']['model']
        #     cam_module = importlib.import_module(camera_model_to_import)
        # except ModuleNotFoundError:
        #     self.logger.error('The model {} for the camera was not found'.format(self.config['camera']['model']))
        #     raise
        # except:
        #     self.logger.exception('Unhandled exception')
        #     raise

        # cam_init_arguments = self.config['camera']['init']

        # if 'extra_args' in self.config['camera']:
        #     self.logger.info('Initializing camera with extra arguments')
        #     self.logger.debug('cam_module.camera({}, {})'.format(cam_init_arguments, self.config['camera']['extra_args']))
        #     self.camera = cam_module.Camera(cam_init_arguments, *self.config['Camera']['extra_args'])
        # else:
        #     self.logger.info('Initializing camera without extra arguments')
        #     self.logger.debug('cam_module.camera({})'.format(cam_init_arguments))
        #     self.camera = cam_module.Camera(cam_init_arguments)

        # self.camera.initialize()
        self.current_width, self.current_height = self.camera.get_size()
        self.logger.info('Camera sensor ROI: {}px X {}px'.format(self.current_width, self.current_height))
        self.max_width, self.max_height = self.camera.get_max_size()
        self.logger.info('Camera sensor size: {}px X {}px'.format(self.max_width, self.max_height))

    def stop_publisher(self):
        """ Puts the proper data to the queue in order to stop the running publisher process
        """
        self.logger.info('Stopping the publisher')
        self.publisher.stop()
        self.stop_subscribers()

    def stop_subscribers(self):
        """ Puts the proper data into every alive subscriber in order to stop it.
        """
        self.logger.info('Stopping the subscribers')
        for event in self.subscriber_events:
            event.set()

        for connection in self._connections:
            if connection['process'].is_alive():
                self.logger.info('Stopping {}'.format(connection['method']))
                connection['event'].set()

    def connect(self, method, topic, *args, **kwargs):
        """ Async method that connects the running publisher to the given method on a specific topic.

        :param method: method that will be connected on a given topic
        :param str topic: the topic that will be used by the subscriber to discriminate what information to collect.
        :param args: extra arguments will be passed to the subscriber, which in turn will pass them to the function
        :param kwargs: extra keyword arguments will be passed to the subscriber, which in turn will pass them to the function
        """
        event = Event()
        self.logger.debug('Arguments: {}'.format(args))
        arguments = [method, topic, event]
        for arg in args:
            arguments.append(arg)

        self.logger.info('Connecting {} on topic {}'.format(method.__name__, topic))
        self.logger.debug('Arguments: {}'.format(args))
        self.logger.debug('KWarguments: {}'.format(kwargs))
        self._connections.append({
            'method':method.__name__,
            'topic': topic,
            'process': Process(target=subscriber, args=arguments, kwargs=kwargs),
            'event': event,
        })
        self._connections[-1]['process'].start()

    def load_configuration(self, filename):
        """ Loads the configuration file in YAML format.

        :param str filename: full path to where the configuration file is located.
        :raises FileNotFoundError: if the file does not exist.
        """
        self.logger.info('Loading configuration file {}'.format(filename))
        try:
            with open(filename, 'r') as f:
                self.config = yaml.safe_load(f)
                self.logger.debug('Config loaded')
                self.logger.debug(self.config)
        except FileNotFoundError:
            self.logger.error('The specified file {} could not be found'.format(filename))
            raise
        except Exception as e:
            self.logger.exception('Unhandled exception')
            raise

    def clear_threads(self):
        """ Keep only the threads that are alive.
        """
        self._threads = [thread for thread in self._threads if thread[1].is_alive()]

    @property
    def num_threads(self):
        return len(self._threads)

    @property
    def connections(self):
        return [conn for conn in self._connections if conn['process'].is_alive()]

    @property
    def alive_threads(self):
        alive_threads = 0
        for thread in self._threads:
            if thread[1].is_alive():
                alive_threads += 1
        return alive_threads

    @property
    def list_alive_threads(self):
        alive_threads = []
        for thread in self._threads:
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
        self.publisher.stop()

    def update_config(self, **kwargs):
        self.logger.info('Updating config')
        self.logger.debug('Config params: {}'.format(kwargs))
        self.config.update(**kwargs)

    def __enter__(self):
        self.set_up()
        return self

    def __exit__(self, *args):
        self.logger.info("Exiting the experiment")
        self.finalize()

        self.logger.debug('Number of open connections: {}'.format(len(self.connections)))
        for event in self.subscriber_events:
            event.set()

        for conn in self.connections:
            self.logger.debug('Waiting for {} to finish'.format(conn['method']))
            conn['process'].join()

        self.logger.info('Finished the base experiment')

        self.publisher.stop()




