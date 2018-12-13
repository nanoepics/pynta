import os
from argparse import ArgumentParser
import logging
from PyQt5.QtWidgets import QApplication

from pynta.model.experiment.nano_cet.win_nanocet import NanoCET
from pynta.util.log import get_logger
from pynta.view.main import MainWindow



def main():
    # logger = get_logger()  # 'pynta.model.experiment.nano_cet.saver'
    # # logger.setLevel(logging.DEBUG)
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.WARNING)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # ch.setFormatter(formatter)
    # logger.addHandler(ch)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    parser = ArgumentParser(description='Start the pyNTA software')
    parser.add_argument("-c", dest="config_file", required=False,
                        help="Path to the configuration file")
    args = parser.parse_args()

    if args.config_file is None:
        config_file = os.path.join(BASE_DIR, 'util', 'example_config.yml')
    else:
        config_file = args.config_file
    exp = NanoCET(config_file)
    exp.initialize_camera()
    app = QApplication([])
    window = MainWindow(exp)
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
