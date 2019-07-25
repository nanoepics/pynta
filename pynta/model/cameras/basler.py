"""
    Basler Camera Model
    ===================
    Model to adapt PyPylon to the needs of Pynta. PyPylon is only a wrapper for Pylon, thus the documentation
    has to be found in the folder where Pylon was installed. It refers only to the C++ documentation, which is
    very extensive, but not necessarily clear.

    Some assumptions
    ----------------
    The program forces software trigger during :meth:`~nanoparticle_tracking.model.cameras.basler.Camera.initialize`.
"""
import logging

from pypylon import pylon

from pynta.model.cameras.base_camera import BaseCamera
from pynta.model.cameras.exceptions import CameraNotFound, WrongCameraState, CameraException
from pynta.util import get_logger
from pynta import Q_

logger = get_logger(__name__)


class Camera(BaseCamera):
    def __init__(self, camera):
        super().__init__(camera)
        self.cam_num = camera
        self.max_width = 0
        self.max_height = 0
        self.logger = get_logger(name=__name__)
        self.mode = None

    def initialize(self):
        """ Initializes the communication with the camera. Get's the maximum and minimum width. It also forces
        the camera to work on Software Trigger.

        .. warning:: It may be useful to integrate with other types of triggers in applications that need to
        synchronize with other hardware.

        """
        logger.debug('Initializing Basler Camera')
        tl_factory = pylon.TlFactory.GetInstance()
        devices = tl_factory.EnumerateDevices()
        if len(devices) == 0:
            raise CameraNotFound('No camera found')

        self.camera = pylon.InstantCamera()
        self.camera.Attach(tl_factory.CreateDevice(devices[self.cam_num]))
        self.camera.Open()

        logger.info(f'Loaded camera {self.camera.GetDeviceInfo().GetModelName()}')

        self.max_width = self.camera.Width.Max
        self.max_height = self.camera.Height.Max
        self.camera.RegisterConfiguration(pylon.SoftwareTriggerConfiguration(), pylon.RegistrationMode_ReplaceAll,
                                          pylon.Cleanup_Delete)
        self.set_acquisition_mode(self.MODE_SINGLE_SHOT)

    def set_acquisition_mode(self, mode):
        self.logger.info(f'Setting acquisition mode to {mode}')
        if mode == self.MODE_CONTINUOUS:
            logger.debug(f'Setting buffer to {self.camera.MaxNumBuffer.Value}')
            self.camera.OutputQueueSize = self.camera.MaxNumBuffer.Value
            self.camera.AcquisitionMode.SetValue('Continuous')
            self.mode = mode
        elif mode == self.MODE_SINGLE_SHOT:
            self.camera.AcquisitionMode.SetValue('SingleFrame')
            self.mode = mode

        self.camera.AcquisitionStart.Execute()

    def setROI(self, X, Y):
        """ Set up the region of interest of the camera. Basler calls this the
        Area of Interest (AOI) in their manuals. Beware that not all cameras allow
        to set the ROI (especially if they are not area sensors).
        Both the corner positions and the width/height need to be multiple of 4.
        Compared to Hamamatsu, Baslers provides a very descriptive error warning.

        """
        width = abs(X[1]-X[0])
        width = int(width-width%4)
        x_pos = int(X[0]-X[0]%4)
        height = int(abs(Y[1]-Y[0]))
        y_pos = int(Y[0]-Y[0]%2)
        if x_pos+width > self.max_width:
            raise CameraException('ROI width bigger than camera area')
        if y_pos+height > self.max_height:
            raise CameraException('ROI height bigger than camera area')

        # First set offset to minimum, to avoid problems when going to a bigger size
        self.clearROI()
        logger.debug(f'Setting width to {width}')
        self.camera.Width.SetValue(width)
        logger.debug(f'Setting X offset to {x_pos}')
        self.camera.OffsetX.SetValue(x_pos)
        logger.debug(f'Setting Height to {height}')
        self.camera.Height.SetValue(height)
        logger.debug(f'Setting Y offset to {y_pos}')
        self.camera.OffsetY.SetValue(y_pos)
        self.X = [x_pos, x_pos+width]
        self.Y = [y_pos, y_pos+width]
        self.width = width
        self.heigth = height
        return width, height

    def clearROI(self):
        self.camera.OffsetX.SetValue(self.camera.OffsetX.Min)
        self.camera.OffsetY.SetValue(self.camera.OffsetY.Min)
        self.camera.Width.SetValue(self.camera.Width.Max)
        self.camera.Height.SetValue(self.camera.Height.Max)

    def GetCCDWidth(self):
        return self.max_width

    def GetCCDHeight(self):
        return self.max_height

    def getSize(self):
        return self.camera.Width.Value, self.camera.Height.Value

    def trigger_camera(self):
        if self.camera.IsGrabbing():
            logger.warning('Triggering an already grabbing camera')
        else:
            if self.mode == self.MODE_CONTINUOUS:
                self.camera.StartGrabbing(pylon.GrabStrategy_OneByOne)
            elif self.mode == self.MODE_SINGLE_SHOT:
                self.camera.StartGrabbing(1)
        self.camera.ExecuteSoftwareTrigger()

    def set_exposure(self, exposure: Q_) -> Q_:
        self.camera.ExposureTime.SetValue(exposure.m_as('us'))
        self.exposure = exposure
        return self.get_exposure()

    def get_exposure(self) -> Q_:
        self.exposure = float(self.camera.ExposureTime.ToString()) * Q_('us')
        return self.exposure

    def read_camera(self):
        if not self.camera.IsGrabbing():
            raise WrongCameraState('You need to trigger the camera before reading from it')

        if self.mode == self.MODE_SINGLE_SHOT:
            grab = self.camera.RetrieveResult(int(self.exposure.m_as('ms')) + 100, pylon.TimeoutHandling_Return)
            img = [grab.Array]
            grab.Release()
            self.camera.StopGrabbing()
        else:
            img = []
            num_buffers = self.camera.NumReadyBuffers.Value
            logger.debug(f'{self.camera.NumQueuedBuffers.Value} frames available')
            if num_buffers:
                img = [None] * num_buffers
                for i in range(num_buffers):
                    grab = self.camera.RetrieveResult(int(self.exposure.m_as('ms')) + 100, pylon.TimeoutHandling_Return)
                    if grab:
                        img[i] = grab.Array
                        grab.Release()
        return [i.T for i in img]  # Transpose to have the correct size

    def stop_camera(self):
        self.camera.StopGrabbing()
        self.camera.AcquisitionStop.Execute()

    def __del__(self):
        self.camera.Close()


if __name__ == '__main__':
    from time import sleep

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.info('Starting Basler')
    basler = Camera(0)
    basler.initialize()
    basler.set_acquisition_mode(basler.MODE_SINGLE_SHOT)
    basler.set_exposure(Q_('.02s'))
    basler.trigger_camera()
    print(len(basler.read_camera()))
    basler.set_acquisition_mode(basler.MODE_CONTINUOUS)
    basler.trigger_camera()
    sleep(1)
    imgs = basler.read_camera()
    print(len(imgs))
