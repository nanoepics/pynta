# -*- coding: utf-8 -*-
"""
    skeleton.py
    ~~~~~~~~~~~

    .. note:: **IMPORTANT** Whatever new function is implemented in a specific model, it should be first declared in the
    laserBase class. In this way the other models will have access to the method and the program will keep running
    (perhaps with non intended behavior though).

    :copyright:  Aquiles Carattino <aquiles@aquicarattino.com>
    :license: AGPLv3, see LICENSE for more details
"""


class DaqBase():
    def __init__(self, dev_number):
        self.dev_number = dev_number

    def analog_input_setup(self, conditions):
        """
        conditions -- a dictionary with the needed parameters for an analog acquisition.
        """
        pass

    def trigger_analog(self, task_number):
        """
        Triggers an analog measurement. It does not read the value.

        conditions -- dictionary with the number of points ot be read
        """
        pass

    def analog_output_setup(self, conditions):
        """
        Sets up an analog output task.

        :param conditions:
        :return:
        """

    def read_analog(self, task_number, conditions):
        """
        Gets the analog values acquired with the triggerAnalog function.
        """
        pass