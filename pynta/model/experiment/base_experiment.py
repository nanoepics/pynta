# -*- coding: utf-8 -*-
"""
    base_experiment.py
    ~~~~~~~~~~~~~~~~~~
    Base Class for the experiments. For the time being it is only a convenience class in order to allow context
    managers. It can evolve into an actually useful strategy to standardize experiments (e.g. how to save data, etc.)

    :copyright:  Aquiles Carattino <aquiles@aquicarattino.com>
    :license: AGPLv3, see LICENSE for more details
"""
import yaml

from pynta.util import get_logger


class BaseExperiment:
    """ Base class to define experiments. Should keep track of the basic methods needed regardless of the experiment
    to be performed. For instance, a way to start and a way to finalize a measurement.
    """
    def __init__(self):
        self.config = {}  # Dictionary storing the configuration of the experiment
        self.logger = get_logger(name=__name__)
        self.async_threads = []

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
        self.async_threads.append([func.__name__, Thread(target=self.snap, args=args, kwargs=kwargs)])
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
        self.finalize()


if __name__ == '__main__':
    with BaseExperiment() as exp:
        print('Success!')
        exp.update_config(timelapse=2, framerate=4)
        print(exp.config)