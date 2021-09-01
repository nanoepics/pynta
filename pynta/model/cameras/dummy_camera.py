# -*- coding: utf-8 -*-
"""
    Dummy Camera Model
    ==================
    Dummy camera class for testing GUI and other functionality. This specific version generates randomly diffusing
    particles. However, the settings are controlled in a different class, :mod:`SimBrownian <pynta.model.cameras.simulate_brownian>`.

    .. TODO:: The camera defines plenty of parameters that are not used or that they are confusing later on. Rasing
        exceptions does not happen even if trying to extend beyond the maximum dimensions of the CCD.

    .. TODO:: The parameters for the simulation of the brownian motion should be made explicitly here, in such a way
        that can be used from within the config file as well.

    .. TODO:: Some of the methods do not return the same datatype as the real models

    :copyright:  Aquiles Carattino <aquiles@uetke.com>
    :license: GPLv3, see LICENSE for more details

"""
import time
import numpy as np
from pynta.model.cameras.simulate_nanospring import SimBrownian
from pynta.util.log import get_logger
from pynta import Q_
from .base_camera import BaseCamera


class Camera(BaseCamera):
    MODE_CONTINUOUS = 1
    MODE_SINGLE_SHOT = 0

    def __init__(self, camera):
        super().__init__(camera)
        self.data_type = np.uint16
        self.xsize = 255
        self.ysize = 200
        self.maxX = 800
        self.maxY = 720
        self.exposure = Q_('10ms')
        self.X = [0, self.maxX-1]
        self.Y = [0, self.maxY-1]
        self.logger = get_logger(name=__name__)
        self.last_frame_t = 0
        self.min_frame_time = 10e-3
    def initialize(self):
        """Initializes the camera.
        """
        self.logger.info('Initializing camera')
        self.maxWidth = self.GetCCDWidth()
        self.maxHeight = self.GetCCDHeight()
        return True

    def trigger_camera(self):
        """Triggers the camera.
        """
        return True

    def set_acquisition_mode(self, mode):
        """
        Set the readout mode of the camera: Single or continuous.

        :param: int mode: One of self.MODE_CONTINUOUS, self.MODE_SINGLE_SHOT
        """
        self.logger.debug('Setting acquisition mode')
        return self.get_acquisition_mode()

    def get_acquisition_mode(self):
        """Returns the acquisition mode, either continuous or single shot.
        """
        return self.MODE_CONTINUOUS

    def acquisition_ready(self):
        """Checks if the acquisition in the camera is over.
        """
        return True

    def set_exposure(self, exposure):
        """Sets the exposure of the camera.
        """
        self.exposure = exposure
        self.sb.time_step = self.exposure.m_as('s')

    def get_exposure(self):
        """Gets the exposure time of the camera.
        """
        return self.exposure

    def read_camera(self):
        
        sample = self.sb.gen_image().astype(self.data_type)
        #sample[10:20, 40:50] = int(127+127*np.sin(moment))  # added this line for intensity tracking testing
        moment = time.time()
        # if self.last_frame_t is not None:
        # print(moment-self.last_frame_t)
        #print("generated a frame at {}".format(moment))
        if moment-self.last_frame_t >= self.min_frame_time:
            self.last_frame_t = moment
            return [sample]
        else:
            sleep_for = self.min_frame_time + self.last_frame_t - moment
            self.last_frame_t = moment
            #print("sleeping for {}".format(sleep_for))
            time.sleep(sleep_for)            
            return [sample]
        # elapsed = time.time() - moment
        # if elapsed > self.exposure.m_as('s'):
            # self.logger.warning('Generating a frame takes longer than exposure time')
        # else:
        # self.logger.debug('Sleeping for {}'.format(self.exposure.m_as('s') - elapsed))
        #time.sleep(self.exposure.m_as('s') - elapsed)  # to simulate exposure time corrected for data generation delay
        

    def set_ROI(self, X, Y):
        """
        Sets up the ROI. Not all cameras are 0-indexed, so this is an important
        place to define the proper ROI.

        :param X: array type with the coordinates for the ROI X[0], X[1]
        :param Y: array type with the coordinates for the ROI Y[0], Y[1]
        :return:
        """
        X = np.sort(X)
        Y = np.sort(Y)
        self.xsize = abs(X[1] - X[0])+1
        self.ysize = abs(Y[1] - Y[0])+1
        # self.sb.resize_view((self.xsize, self.ysize))
        self.X = X
        self.Y = Y
        self.X[1] -= 1
        self.Y[1] -= 1
        self.sb = SimBrownian((self.xsize, self.ysize))
        return self.get_size()

    def get_size(self):
        """
        :return: Returns the size in pixels of the image being acquired. This is useful for checking the ROI settings.
        """

        return self.xsize, self.ysize

    def getSerialNumber(self):
        """Returns the serial number of the camera.
        """
        return "Serial Number"

    def GetCCDWidth(self):
        """
        :return: The CCD width in pixels
        """
        return self.maxX

    def GetCCDHeight(self):
        """
        :return: The CCD height in pixels
        """
        return self.maxY

    def set_binning(self, xbin, ybin):
        """Sets the binning of the camera if supported. Has to check if binning in X/Y can be different or not, etc.

        :param: xbin: binning in x
        :param: ybin: binning in y
        """
        self.xbin = xbin
        self.ybin = ybin

    def stopAcq(self):
        pass

    def stop_camera(self):
        pass
