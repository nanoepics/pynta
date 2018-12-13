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
    parser = ArgumentParser(description='Start the pyNTA software')
    parser.add_argument("-c", dest="config_file", required=True,
                        help="Path to the configuration file")
    args = parser.parse_args()

    exp = NanoCET(args.config_file)
    exp.initialize_camera()
    app = QApplication([])
    window = MainWindow(exp)
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
