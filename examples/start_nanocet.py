from time import sleep
import logging
from pynta.model.experiment.nano_cet.nano_cet import NanoCET
from pynta.util.log import get_logger

logger = logging.getLogger('pynta.model.experiment.nano_cet.worker_saver')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


with NanoCET('config/nanocet.yml') as exp:
    sleep(2)
    exp.initialize_camera()
    exp.connect(exp.add_to_stream_queue, 'free_run')
    exp.save_stream()
    sleep(2)
    exp.start_free_run()
    for i in range(10):
        sleep(1)
    # exp.keep_acquiring = False
    exp.stop_save_stream()
    sleep(2)

print('Finished')