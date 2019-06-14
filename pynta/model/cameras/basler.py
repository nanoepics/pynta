"""
    Basler Camera Model
    ===================
    Model to adapt PyPylon to the needs of Pynta. PyPylon is only a wrapper for Pylon, thus the documentation
    has to be found in the folder where Pylon was installed. It refers only to the C++ documentation, which is
    very extensive, but not necessarily clear.

    Some assumptions
    ----------------
    The program forces software trigger during `~meth:Camera.initialize`.
"""
import logging

from pypylon import pylon

from pynta.model.cameras.base_camera import BaseCamera
from pynta.util import get_logger

logger = get_logger(__name__)


class Camera(BaseCamera):
    def __init__(self, camera):
        super().__init__(camera)
        self.cam_num = camera
        self.max_width = 0
        self.max_height = 0
        self.logger = get_logger(name=__name__)

    def initialize(self):
        """ Initializes the communication with the camera. Pylon is very convoluted and pypylon is just
        a wrapper.
        """
        logger.debug('Initializing Basler Camera')
        tl_factory = pylon.TlFactory.GetInstance()
        devices = tl_factory.EnumerateDevices()
        if len(devices) == 0:
            raise pylon.RUNTIME_EXCEPTION("No camera present.")

        self.camera = pylon.InstantCamera()
        self.camera.Attach(tl_factory.CreateDevice(devices[self.cam_num]))

        logger.info(f'Loaded camera {self.camera.GetDeviceInfo().GetModelName()}')

        nodemap = self.camera.GetNodeMap()
        self.max_width = nodemap.GetNode('Width').Max
        self.max_height = nodemap.GetNode('Height').Max
        self.camera.RegisterConfiguration(pylon.SoftwareTriggerConfiguration(), pylon.RegistrationMode_ReplaceAll,
                                     pylon.Cleanup_Delete)

    def set_acquisiton_mode(self, mode):
        if mode == self.MODE_CONTINUOUS:
            pass
        elif mode == self.MODE_SINGLE_SHOT:
            pass




if __name__ == '__main__':

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.info('Starting Basler')
    basler = Camera(0)
    basler.initialize()


