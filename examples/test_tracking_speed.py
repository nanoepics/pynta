import os
from multiprocessing import freeze_support
from time import sleep

from pynta import BASE_DIR
from pynta.model.experiment.nanoparticle_tracking.np_tracking import NPTracking



if __name__ == "__main__":
    freeze_support()
    config_file = os.path.join(BASE_DIR, 'util', 'example_config.yml')
    with NPTracking(config_file) as exp:
        exp.initialize_camera()
        exp.start_free_run()
        while exp.camera.sb.current_frame<exp.camera.sb.frames_to_accumulate:
            sleep(5)
        exp.stop_free_run()
        exp.start_tracking()
        exp.start_free_run()
        print('Plase wait 30 seconds')
        sleep(30)
        exp.stop_tracking()
        exp.stop_free_run()
        exp.finalize()
