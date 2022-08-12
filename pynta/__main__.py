import os
import time
from argparse import ArgumentParser
import logging
from PyQt5.QtWidgets import QApplication

#from pynta.model.experiment.nanospring_tracking.ns_tracking import NSTracking as Experiment

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('PyQt5').setLevel(logging.INFO)  # to prevent PyQt5 from flooding the console, set that logger to INFO
logging.getLogger('h5py').setLevel(logging.INFO)  # to prevent PyQt5 from flooding the console, set that logger to INFO

import pynta
from pynta.util.log import get_logger
#from pynta.view.main import MainWindow

def main():
    logger = get_logger()  # 'nanoparticle_tracking.model.experiment.nanoparticle_tracking.saver'
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    parser = ArgumentParser(description='Start the pyNTA software')
    parser.add_argument("-c", dest="config_file", required=False,
                        help="Path to the configuration file")
    args = parser.parse_args()

    if args.config_file is None:
        config_file = os.path.join(pynta.package_path, 'user', 'user_config.yml')
        if not os.path.exists(config_file):
            import shutil
            shutil.copy(os.path.join(pynta.package_path, 'util', 'example_config.yml'), config_file)
            print('\n\n******************************\n\nA user config file was created in {}\nThis file is ignored by git. \nIt will be loaded by default.\nPlease only modify that config file. \nMake sure to change the saving path.\n\n******************************\n\n'.format(config_file))
    else:
        config_file = args.config_file

    try:
        from pynta.user import software_config
    except:
        software_config_file = os.path.join(pynta.package_path, 'user', 'software_config.py')
        if not os.path.exists(software_config_file):
            import shutil
            shutil.copy(os.path.join(pynta.package_path, 'util', 'software_config.py'), software_config_file)
            print('\n\n******************************\n\nA software config file was created in {}\nThis file is ignored by git. \nIt will be loaded by default.\nPlease only modify that software config file.\n\n******************************\n\n'.format(software_config_file))
            time.sleep(1)
            import imp, sys
            imp.reload(sys.modules['pynta'])
            # from importlib import import_module
            # software_config = import_module('pynta.user.software_config')

        from pynta.user import software_config
    exp = software_config.Experiment(config_file)

    # exp = Experiment(config_file)
    # if exp.gui_file() is None:
    #     # window_builder = import_module('pynta.view.main')
    #     import pynta.view.main as window_builder
    # else:
    #     window_builder = import_module('pynta.view.'+ exp.gui_file())


    app = QApplication([])
    window = software_config.MainWindow(exp)
    # window = window_builder.MainWindow(exp)
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
