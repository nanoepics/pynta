from time import sleep
import logging

from pynta.model.experiment.nano_cet.exceptions import NanoCETException
from pynta.model.experiment.nano_cet.nano_cet import NanoCET
from pynta.util.log import get_logger

logger = logging.getLogger()#'pynta.model.experiment.nano_cet.worker_saver')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

with NanoCET('config/nanocet.yml') as exp:
    sleep(2)
    exp.initialize_camera()
    # exp.connect(exp.add_to_stream_queue, 'free_run')
    exp.connect(exp.calculate_positions_image, 'free_run')
    # exp.connect(exp.link_trajecktories, 'trackpy')
    exp.connect(exp.locations_queue, 'trackpy')
    # exp.save_stream()
    sleep(2)
    exp.start_free_run()
    for i in range(10):
        sleep(1)
    # exp.stop_save_stream()
    sleep(2)
    exp.calculate_positions_image(None)

print('Finished')