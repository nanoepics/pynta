import logging
from time import sleep

from PyQt5.QtWidgets import QApplication

from pynta.model.experiment.nano_cet.motor_test import MotorTestExperiment
from pynta.util import get_logger
from pynta.view.GUI.camera_focusing import CameraFocusing

logger = get_logger()#'pynta.model.experiment.nano_cet.worker_saver')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

if __name__ == '__main__':
    with MotorTestExperiment('config/nanocet.yml') as exp:
        sleep(1)
        exp.initialize_arduino()
        sleep(1)
        app = QApplication([])
        window = CameraFocusing(exp)
        window.show()
        app.exec()