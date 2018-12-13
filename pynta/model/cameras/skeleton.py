# -*- coding: utf-8 -*-
"""
    skeleton.py
    ~~~~~~~~~~~~
    Camera class with the skeleton functions. Important to keep track of the methods that are
    exposed to the View. The class cameraBase should be subclassed when developing new Models. This ensures that all the methods are automatically inherited and there is no breaks downstream.

    .. note:: **IMPORTANT** Whatever new function is implemented in a specific model, it should be first declared in the cameraBase class. In this way the other models will have access to the method and the program will keep running (perhaps with non intended behavior though).

    :copyright:  Aquiles Carattino <aquiles@aquicarattino.com>
    :license: GPLv3, see LICENSE for more details
"""
import numpy as np
from pynta.util.log import get_logger
from pynta import Q_


class cameraBase:
    MODE_CONTINUOUS = 1
    MODE_SINGLE_SHOT = 0

    def __init__(self, camera):
        self.camera = camera
        self.running = False
        self.maxWidth = 0
        self.maxHeight = 0
        self.exposure = 0
        self.config = {}
        self.data_type = np.uint16 # The data type that the camera generates when acquiring images. It is very important to have it available in order to create the buffer and saving to disk.

        self.logger = get_logger(name=__name__)

    def configure(self, properties):
        self.logger.info('Updating config')
        update_cam = False
        update_roi = False
        update_exposure = False
        update_binning = True
        for k in properties:
            new_prop = properties[k]
            self.logger.debug('Updating {} to {}'.format(k, new_prop))

            update_cam = True
            if k in self.config:
                old_prop = self.config[k]
                if new_prop != old_prop:
                    update_cam = True
            else:
                update_cam = True

            if update_cam:
                if k in ['roi_x1', 'roi_x2', 'roi_y1', 'roi_y2']:
                    update_roi = True
                elif k == 'exposure_time':
                    update_exposure = True
                elif k in ['binning_x', 'binning_y']:
                    update_binning = True

        if update_cam:
            if update_roi:

                X = np.sort([properties['roi_x1'], properties['roi_x2']])
                Y = np.sort([properties['roi_y1'], properties['roi_y2']])
                self.setROI(X, Y)
                self.config.update({'roi_x1': X[0],
                                    'roi_x2': X[1],
                                    'roi_y1': Y[0],
                                    'roi_y2': Y[1]})

            if update_exposure:
                exposure = Q_(properties['exposure_time'])
                new_exp = self.setExposure(exposure)
                self.config['exposure_time'] = new_exp

            if update_binning:
                self.setBinning(properties['binning_x'], properties['binning_y'])
                self.config.update({'binning_x': properties['binning_x'],
                                    'binning_y': properties['binning_y']})

    def initializeCamera(self):
        """
        Initializes the camera.
        """
        self.maxWidth = self.GetCCDWidth()
        self.maxHeight = self.GetCCDHeight()
        return True

    def triggerCamera(self):
        """
        Triggers the camera.
        """
        print("Not Implemented")

    def setAcquisitionMode(self, mode):
        """
        Set the readout mode of the camera: Single or continuous.
        :param int mode: One of self.MODE_CONTINUOUS, self.MODE_SINGLE_SHOT
        :return:
        """
        self.mode = mode

    def getAcquisitionMode(self):
        """
        Returns the acquisition mode, either continuous or single shot.
        """
        return self.mode

    def acquisitionReady(self):
        """
        Checks if the acquisition in the camera is over.
        """
        print("Not Implemented")

    def setExposure(self, exposure):
        """
        Sets the exposure of the camera.
        """
        self.exposure = exposure

    def getExposure(self):
        """
        Gets the exposure time of the camera.
        """
        return self.exposure

    def readCamera(self):
        """
        Reads the camera
        """
        print("Not Implemented")

    def setROI(self, X, Y):
        """ Sets up the ROI. Not all cameras are 0-indexed, so this is an important
        place to define the proper ROI.

        :param list X: array type with the coordinates for the ROI X[0], X[1]
        :param list Y: array type with the coordinates for the ROI Y[0], Y[1]
        :return: X, Y lists with the current ROI information
        """
        return X, Y

    def clearROI(self):
        """
        Clears the ROI from the camera.
        """
        self.setROI(self.maxWidth, self.maxHeight)

    def getSize(self):
        """Returns the size in pixels of the image being acquired. This is useful for checking the ROI settings.
        """
        print("Not Implemented")

    def getSerialNumber(self):
        """Returns the serial number of the camera.
        """
        print("Not Implemented")

    def GetCCDWidth(self):
        """
        Returns the CCD width in pixels
        """
        print("Not Implemented")

    def GetCCDHeight(self):
        """
        Returns: the CCD height in pixels
        """
        print("Not Implemented")

    def stopAcq(self):
        """Stops the acquisition without closing the connection to the camera."""
        print("Not Implemented")

    def setBinning(self, xbin, ybin):
        """
        Sets the binning of the camera if supported. Has to check if binning in X/Y can be different or not, etc.

        :param xbin:
        :param ybin:
        :return:
        """
        print("Not Implemented")

    def stopCamera(self):
        """Stops the acquisition and closes the connection with the camera.
        """
        try:
            # Closing the camera
            print("Not Implemented")
        except:
            # Monitor failed to close
            print("Not Implemented")
