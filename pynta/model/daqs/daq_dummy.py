# -*- coding: utf-8 -*-
"""
    Dummy DAQ
    =========
    DAQ model for testing GUI and other functionalities. Based on the skeleton. It does not interact with any real
    device, it just generates random data and accepts inputs which have no effect.

    :copyright:  Aquiles Carattino <aquiles@uetke.com>
    :license: GPLv3, see LICENSE for more details
"""
from pynta.util import get_logger
from .skeleton import DaqBase

logger = get_logger(__name__)


class DAQDummy(DaqBase):
    def __init__(self, dev_number=None):
        super().__init__(dev_number)
        logger.info('Initialized device with number: %s' % dev_number)
        self.test_value = 0

    def triggerAnalog(self, conditions):
        """Triggers an analog measurement. It does not read the value.
        conditions -- a dictionary with the needed parameters for an analog acquisition.
        """
        pass

    def getAnalog(self,conditions):
        """Gets the analog values acquired with the triggerAnalog function.
        conditions -- dictionary with the number of points ot be read
        """
        pass


    def startMonitor(self,conditions):
        """Starts continuous acquisition of the specified channels with the specified timing interval.
        conditions['devs'] -- list of devices to monitor
        conditions['accuracy'] -- accuracy for the monitor. If not defined defaults to 0.1s
        """
        pass

    def readMonitor(self):
        """Reads the monitor values of all the channels specified.
        """
        pass

    def stopMonitor(self):
        """Stops all the tasks related to the monitor.
        """
        pass

    def fastTimetrace(self,conditions):
        """ Acquires a fast timetrace of the selected devices.
        conditions['devs'] -- list of devices to monitor
        conditions['accuracy'] -- accuracy in milliseconds.
        conditions['time'] -- total time of acquisition for each channel in seconds.
        """
        pass
