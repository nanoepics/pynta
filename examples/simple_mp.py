import logging
from multiprocessing import freeze_support
from time import sleep

from pynta.model.experiment.base_experiment import BaseExperiment
from pynta.util import get_logger

logger = get_logger()#'pynta.model.experiment.nano_cet.worker_saver')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


if __name__ == "__main__":
    freeze_support()
    with BaseExperiment() as exp:

        sleep(5)