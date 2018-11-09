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