import logging
from time import sleep

from pynta.model.experiment.nano_cet.win_nanocet import NanoCET
from pynta.util.log import get_logger


logger = get_logger()  # 'pynta.model.experiment.nano_cet.saver'
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


if __name__ == '__main__':
    with NanoCET('config/nanocet.yml') as exp:
        sleep(1)
        # exp.connect(calculate_positions_image, 'free_run', exp.publisher_queue, **exp.config['tracking']['locate'])
        # exp.connect(add_to_save_queue, 'free_run', exp.saver_queue)
        # exp.connect(add_linking_queue, 'trackpy_locations', exp.locations_queue)
        # exp.connect(add_links_to_queue, 'particle_links', exp.tracks_queue)
        exp.initialize_camera()
        # exp.link_particles()
        exp.save_stream()
        sleep(1)
        exp.start_free_run()
        logger.info('Going to sleep for 5 seconds')
        sleep(5)
        logger.info('Keep acquiring set to false')
        exp.keep_acquiring = False
        logger.info('Sleeping for 2 seconds')
        sleep(2)
        # exp.plot_histogram()