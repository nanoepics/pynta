import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget


class ConfigTrackingWidget(QWidget):

    apply_config = pyqtSignal(dict)
    flags = Qt.WindowStaysOnTopHint

    def __init__(self, parent=None):
        super().__init__(parent, flags=self.flags)
        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'designer', 'tracking_config.ui'), self)
        self._config = None

        self.button_apply.clicked.connect(self.get_config)
        self.button_cancel.clicked.connect(self.revert_changes)

    def update_config(self, config):
        """
        :param config: Dictionary with the new values
        :type config: dict
        """
        self.line_diameter.setText(str(config['locate']['diameter']))
        self.line_min_mass.setText(str(config['locate']['minmass']))
        self.check_invert.setChecked(config['locate']['invert'])

        self.line_memory.setText(str(config['link']['memory']))
        self.line_search_range.setText(str(config['link']['search_range']))

        self.line_min_length.setText(str(config['process']['min_traj_length']))
        self.line_calibration.setText(str(config['process']['um_pixel']))
        self.line_min_mass_2.setText(str(config['process']['min_mass']))
        self.line_max_size.setText(str(config['process']['max_size']))
        self.line_max_ecc.setText(str(config['process']['max_ecc']))
        self.check_drift.setChecked(config['process']['compute_drift'])
        self._config = config

    def get_config(self):
        config = dict(
            locate=dict(
                diameter=int(self.line_diameter.text()),
                minmass=float(self.line_min_mass.text()),
                invert=self.check_invert.isChecked(),
            ),
            link=dict(
                memory=int(self.line_memory.text()),
                search_range=float(self.line_search_range.text())

            ),
            process=dict(
                min_traj_length=int(self.line_min_length.text()),
                um_pixel=float(self.line_calibration.text()),
                min_mass=float(self.line_min_mass_2.text()),
                max_size=float(self.line_max_size.text()),
                max_ecc=float(self.line_max_ecc.text()),
                compute_drift=self.check_drift.isChecked(),
            )
        )
        self._config = config
        self.apply_config.emit(config)
        return self._config

    def revert_changes(self):
        self.update_config(self._config)

    def print_config(self, config):
        print(config)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    config = {'locate':
                  {'diameter': 10,
                   'minmass': 100,
                   'invert': True},
              'link':
                  {'memory': 3,
                   'search_range': 4
                   },
              'process':
                  {'min_traj_length': 20,
                   'um_pixel': 1,
                   'min_mass': 200,
                   'max_size': 10,
                    'max_ecc': 0.2,
                   'compute_drift': False,
                  }
              }

    app = QApplication([])
    win = ConfigTrackingWidget()
    win.apply_config.connect(win.print_config)
    win.update_config(config)
    win.show()
    app.exec()
