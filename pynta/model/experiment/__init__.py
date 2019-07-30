# -*- coding: utf-8 -*-
"""
    Experiment Models
    =================
    Experiment models make explicit the different steps needed to perform a measurement. The Base Experiment class
    defines some methods that are transversal to all experiments (such as loading a configuration file) but individual
    experiment models can overwrite this methods to develop custom solutions.

    Moreover, PyNTA introduces the PUB/SUB pattern in order to exchange information between different parts of the
    program in a flexible and efficient way. You can find more information on :mod:`~pynta.model.experiment.publisher`
    and :mod:`~pynta.model.experiment.subscriber`.

    :copyright:  Aquiles Carattino <aquiles@uetke.com>
    :license: GPLv3, see LICENSE for more details
"""
from pynta.model.experiment.config import Config

config = Config()