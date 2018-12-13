# -*- coding: utf-8 -*-
"""
    psi.py
    ~~~~~~

    Model for Photonic Science GEV Cameras. The model just implements the basic methods defined in the
    :meth:`~pynta.model.cameras.skeleton.cameraBase` using a Photonic Sicence camera. The controller for this
    camera is :mod:`~pynta.controller.devices.photonicscience`

    :copyright:  Aquiles Carattino <aquiles@aquicarattino.com>
    :license: GPLv3, see LICENSE for more details
"""
import numpy as np

from pynta.controller.devices.photonicscience.scmoscam import GEVSCMOS
from .skeleton import cameraBase

NUMPY_MODES = {"L": np.uint8, "I;16": np.uint16}


class camera(cameraBase):
    def __init__(self, camera):
        self.cam_num = camera
        self.camera = GEVSCMOS(camera, 'SCMOS')
        self.running = False

    def initializeCamera(self):
        """
        Initializes the camera.

        .. todo:: :meth:`UUTrack.Controller.devices.PhotonicScience.scmoscam.GEVSCMOS.SetGainMode` behaves unexpectedly.
            One is forced to set the gain mode twice to have it right. So far, this is the only way to prevent the
            *weird lines* from appearing. Checking the meaning of the gains is a **must**.

        """
        self.camera.Open()
        self.maxSize = self.camera.UpdateSizeMax()
        self.camera.SetClockSpeed('50MHz')
        self.camera.SetGainMode(
            'gain1+30_Hardware')  # Do not change! It is needed for avoiding weird lines in the images. The gain can be changed at the end of this method
        self.camera.SetTrigger("FreeRunning")
        self.camera.EnableAutoLevel(0)
        self.camera.SetExposure(10, "Millisec")
        self.triggerCamera()
        size = self.getSize()
        self.maxWidth = size[0]
        self.maxHeight = size[1]
        self.camera.SetGainMode("gain30")  # Change the gain here! Check scmoscam.py for information

    def triggerCamera(self):
        """Triggers the camera.
        """
        self.camera.Snap()

    def setExposure(self, exposure):
        """Sets the exposure of the camera.

        .. todo:: Include units for ensuring the proper exposure time is being set.
        """
        exposure = exposure * 1000  # in order to always use microseconds
        # while self.camera.GetStatus(): # Wait until exposure is finished.
        self.camera.SetExposure(np.int(exposure), 'Microsec')

    def readCamera(self):
        """Reads the camera
        """
        if self.getAcquisitionMode() == self.MODE_CONTINUOUS:
            self.triggerCamera()
        size, data = self.camera.GetImage()
        w, h = size
        mode = self.camera.GetMode()
        img = np.frombuffer(data, NUMPY_MODES[mode]).reshape((h, w))
        img = np.array(img)
        return np.transpose(img)

    def setROI(self, X, Y):
        """Sets up the ROI.
        """
        X -= 1
        Y -= 1
        # Left, top, right, bottom
        l = np.int(X[0])
        t = np.int(Y[0])
        r = np.int(X[1])
        b = np.int(Y[1])
        self.camera.SetSubArea(l, t, r, b)
        return self.camera.GetSize()

    def getSize(self):
        """Returns the size in pixels of the image being acquired.
        """
        return self.camera.GetSize()

    def setupCamera(self, params):
        """Setups the camera with the given parameters.

        - params['exposureTime']
        - params['binning']
        - params['gain']
        - params['frequency']
        - params['ROI']

        .. todo:: not implemented
        """
        pass

    def getParameters(self):
        """Returns all the parameters passed to the camera, such as exposure time,
        ROI, etc. Not necessarily the parameters go to the hardware, it may be
        that some are just software related.

        :return dict: keyword => value.

        .. todo:: Implement this method
        """
        pass

    def GetCCDWidth(self):
        """Gets the CCD width."""
        return self.getSize()[0]

    def GetCCDHeight(self):
        """Gets the CCD height."""
        return self.getSize()[1]

    def stopAcq(self):
        """Stop the acquisition even if ongoing."""
        self.camera.AbortSnap()

    def stopCamera(self):
        """Stops the acquisition and closes the camera. This has to be called before quitting the program.
        """
        self.camera.AbortSnap()
        self.camera.Close()