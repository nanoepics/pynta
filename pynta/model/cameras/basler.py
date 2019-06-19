"""
    Basler Camera Model
    ===================
    Model to adapt PyPylon to the needs of Pynta. PyPylon is only a wrapper for Pylon, thus the documentation
    has to be found in the folder where Pylon was installed. It refers only to the C++ documentation, which is
    very extensive, but not necessarily clear.

    Some assumptions
    ----------------
    The program forces software trigger during :meth:`~pynta.model.cameras.basler.Camera.initialize`.
"""
import logging

from pypylon import pylon

from pynta.model.cameras.base_camera import BaseCamera
from pynta.model.cameras.exceptions import CameraNotFound, WrongCameraState
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

    def trigger_camera(self):
        if self.camera.IsGrabbing():
            logger.warning('Triggering an already grabbing camera')
        else:
            if self.mode == self.MODE_CONTINUOUS:
                self.camera.StartGrabbing(pylon.GrabStrategy_OneByOne)
            elif self.mode == self.MODE_SINGLE_SHOT:
                self.camera.StartGrabbing(1)
        self.camera.ExecuteSoftwareTrigger()

    def set_exposure(self, exposure: Q_) -> None:
        self.camera.ExposureTime.SetValue(exposure.m_as('us'))
        self.exposure = exposure
        return self.get_exposure()

    def get_exposure(self) -> Q_:
        self.exposure = int(self.camera.ExposureTimeRaw.ToString()) * Q_('us')
        return self.exposure

    def read_camera(self):
        if not self.camera.IsGrabbing():
            raise WrongCameraState('You need to trigger the camera before reading from it')

        if self.mode == self.MODE_SINGLE_SHOT:
            grab = self.camera.RetrieveResult(int(self.exposure.m_as('ms'))+100, pylon.TimeoutHandling_Return)
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
                    grab = self.camera.RetrieveResult(int(self.exposure.m_as('ms'))+100, pylon.TimeoutHandling_Return)
                    if grab:
                        img[i] = grab.Array
                        grab.Release()
        return img

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


