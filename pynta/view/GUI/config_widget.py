"""
    UUTrack.View.Monitor.config_widget.py
    ===================================
    Simple widget for storing the parameters of the :mod:`UUTrack.Model._session`. It creates and populates tree thanks to the :meth:`UUTrack.Model._session._session.getParams`.
    The widget has two buttons, one that updates the session by emitting a `signal` to the main thread and another the repopulates the tree whith the available parameters.

    .. todo:: Remove the printing to screen of the parameters once the debugging is done.

    .. sectionauthor:: Aquiles Carattino <aquiles@aquicarattino.com>
"""
import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget


class ConfigWidget(QWidget):
    """Widget for configuring the main parameters of the camera.
    """
    flags = Qt.WindowStaysOnTopHint
    apply_config = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent, flags=self.flags)
        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'designer', 'config_general.ui'), self)
        self.logging_levels = {
            'Nothing': 0,
            'Debug': 1,
            'Info': 2,
            'Warning': 3,
            'Error': 4,
        }

        self.levels_logging = dict(zip(self.logging_levels.values(), self.logging_levels.keys()))

        self._config = None
        self.apply_button.clicked.connect(self.get_config)
        self.cancel_button.clicked.connect(self.revert_changes)

    def update_config(self, config):
        """
        :param config: Dictionary with the new values
        :type config: dict
        """

        self.camera_model.setText(config['camera']['model'])
        self.camera_init.setText(str(config['camera']['init']))
        self.camera_camera_model.setText(config['camera']['model_camera'])
        self.camera_exposure_time.setText(config['camera']['exposure_time'])
        self.camera_binning_x.setText(str(config['camera']['binning_x']))
        self.camera_binning_y.setText(str(config['camera']['binning_y']))
        self.camera_roi_x1.setText(str(config['camera']['roi_x1']))
        self.camera_roi_x2.setText(str(config['camera']['roi_x2']))
        self.camera_roi_y1.setText(str(config['camera']['roi_y1']))
        self.camera_roi_y2.setText(str(config['camera']['roi_y2']))
        self.camera_background.setText(config['camera']['background'])

        self.saving_directory.setText(config['saving']['directory'])
        self.saving_filename_photo.setText(config['saving']['filename_photo'])
        self.saving_filename_video.setText(config['saving']['filename_video'])
        self.saving_filename_tracks.setText(config['saving']['filename_tracks'])
        self.saving_filename_log.setText(config['saving']['filename_log'])
        self.saving_max_memory.setText(str(config['saving']['max_memory']))

        self.other_user_name.setText(config['user']['name'])
        self.gui_refresh_time.setText(str(config['GUI']['refresh_time']))

        self.logging_level.setCurrentIndex(self.logging_levels[config['debug']['logging_level']])
        self._config = config

    def get_config(self):
        config = dict(
            camera=dict(
                model=self.camera_model.text(),
                init=self.camera_init.text(),
                model_camera=self.camera_camera_model.text(),
                exposure_time=self.camera_exposure_time.text(),
                binning_x=self.camera_binning_x.text(),
                binning_y=self.camera_binning_y.text(),
                roi_x1=int(self.camera_roi_x1.text()),
                roi_x2=int(self.camera_roi_x2.text()),
                roi_y1=int(self.camera_roi_y1.text()),
                roi_y2=int(self.camera_roi_y2.text()),
                background=self.camera_background.text()
            ),
            saving=dict(
                directory=self.saving_directory.text(),
                filename_photo=self.saving_filename_photo.text(),
                filename_video=self.saving_filename_video.text(),
                filename_tracks=self.saving_filename_tracks.text(),
                filename_log=self.saving_filename_log.text(),
                max_memory=int(self.saving_max_memory.text())
            ),
            user=dict(
                name=self.other_user_name.text()
            ),
            GUI=dict(
                refresh_time=int(self.gui_refresh_time.text())
            ),
            debug=dict(
                logging_level=self.levels_logging[self.logging_level.currentIndex()]
            )
        )

        self._config = config
        self.apply_config.emit(config)
        return self._config

    def revert_changes(self):
        self.update_config(self._config)
