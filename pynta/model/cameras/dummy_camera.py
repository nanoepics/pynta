# -*- coding: utf-8 -*-
"""
    dummyCamera.py
    ~~~~~~~~~~~~~~
    Dummy camera class for testing GUI and other functionality. Based on the skeleton.

    :copyright:  Aquiles Carattino <aquiles@aquicarattino.com>
    :license: AGPLv3, see LICENSE for more details
"""
import time
import numpy as np
from .simulate_brownian import SimBrownian
# from lantz import Q_
from .skeleton import cameraBase


class camera(cameraBase):
    MODE_CONTINUOUS = 1
    MODE_SINGLE_SHOT = 0

    def __init__(self, camera):
        self.camera = camera
        self.running = False
        self.xsize = 600
        self.ysize = 250
        self.maxX = 600
        self.maxY = 250
        self.exposure = 0

    def initializeCamera(self):
        """Initializes the camera.
        """
        print('Initializing camera')
        self.maxWidth = self.GetCCDWidth()
        self.maxHeight = self.GetCCDHeight()
        self.sb = SimBrownian([self.xsize, self.ysize])
        return True

    def triggerCamera(self):
        """Triggers the camera.
        """
        return True

    def setAcquisitionMode(self, mode):
        """
        Set the readout mode of the camera: Single or continuous.

        :param: int mode: One of self.MODE_CONTINUOUS, self.MODE_SINGLE_SHOT
        """
        print('Setting acquisition mode')
        return self.getAcquisitionMode()

    def getAcquisitionMode(self):
        """Returns the acquisition mode, either continuous or single shot.
        """
        return self.MODE_CONTINUOUS

    def acquisitionReady(self):
        """Checks if the acquisition in the camera is over.
        """
        return True

    def setExposure(self, exposure):
        """Sets the exposure of the camera.
        """
        self.exposure = exposure * Q_('s')
        return exposure

    def getExposure(self):
        """Gets the exposure time of the camera.
        """
        return self.exposure

    def readCamera(self):
        X, Y = self.getSize()
        moment = time.time()
        self.sb.nextRandomStep()  # creates a next random step according to parameters in SimulateBrownian.py
        sample = self.sb.genImage()
        sample = sample.astype('uint16')
        elapsed = time.time() - moment
        try:
            time.sleep(
                self.exposure.magnitude / 1000 - elapsed)  # to simulate exposure time corrected for data generation delay
        except:
            time.sleep(0)
        return sample

    def setROI(self, X, Y):
        """
        Sets up the ROI. Not all cameras are 0-indexed, so this is an important
        place to define the proper ROI.

        :param X: array type with the coordinates for the ROI X[0], X[1]
        :param Y: array type with the coordinates for the ROI Y[0], Y[1]
        :return:
        """
        self.xsize = abs(X[1] - X[0])
        self.ysize = abs(Y[1] - Y[0])
        self.sb.resizeView((self.xsize, self.ysize))
        return self.getSize()

    def getSize(self):
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

    def setBinning(self, xbin, ybin):
        """Sets the binning of the camera if supported. Has to check if binning in X/Y can be different or not, etc.

        :param: xbin: binning in x
        :param: ybin: binning in y
        """
        self.xbin = xbin
        self.ybin = ybin
        pass

    def stopAcq(self):
        """ Stops the acquisition

        :return: bool True: returns true
        """
        return True

    def stopCamera(self):
        """Stops the acquisition and closes the connection with the camera.
        """
        try:
            # Closing the camera
            return True
        except:
            # Monitor failed to close
            return False