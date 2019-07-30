# -*- coding: utf-8 -*-
"""
    Experiment Configuration
    ========================
    Class which holds some parameters that need to be used throughout the lifetime of a program. Keeping them in a
    separate class gives great flexibility, because it allows to overwrite values at run time.

    .. TODO:: Changes to config at runtime will have no effect on other processes. Find a way in which config can
              broadcast itself to all the instances of the class

    :copyright:  Aquiles Carattino <aquiles@uetke.com>
    :license: GPLv3, see LICENSE for more details
"""
from pynta.util import get_logger


logger = get_logger(__name__)

class Config:
    def __init__(self):
        self.zmq_port = 5555

    def __setattr__(self, key, value):
        logger.debug(f'Setting {key} to {value}')
        super().__setattr__(key, value)