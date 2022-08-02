"""
    Configuration Widget
    ====================
    Simple widget for storing the parameters of the :mod:`UUTrack.Model._session`. It creates and populates tree thanks to the :meth:`UUTrack.Model._session._session.getParams`.
    The widget has two buttons, one that updates the session by emitting a `signal` to the main thread and another the repopulates the tree whith the available parameters.

    .. todo:: Remove the printing to screen of the parameters once the debugging is done.

    .. sectionauthor:: Aquiles Carattino <aquiles@uetke.com>
    Last modified by Aron Opheij on 2021-04-26
"""
import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QTextEdit, QMessageBox, QStatusBar
import yaml


# class ConfigWidget(QWidget):
#     """Widget for configuring the main parameters of the camera.
#     """
#     flags = Qt.WindowStaysOnTopHint
#     apply_config = pyqtSignal(dict)
#
#     def __init__(self, parent=None):
#         super().__init__(parent, flags=self.flags)
#         uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'designer', 'config_general.ui'), self)
#         self.logging_levels = {
#             'Nothing': 0,
#             'Debug': 1,
#             'Info': 2,
#             'Warning': 3,
#             'Error': 4,
#         }
#
#         self.levels_logging = dict(zip(self.logging_levels.values(), self.logging_levels.keys()))
#
#         self._config = None
#         self.apply_button.clicked.connect(self.apply)
#         self.cancel_button.clicked.connect(self.revert_changes)
#
#         self.config_tabs.currentChanged.connect(self.tab_changed)
#         self.font = QFont("Courier New", 10)
#
#         self._temp_conf = {}
#         self.txt.setLineWrapMode(QTextEdit.NoWrap)
#         self.txt.setFont(self.font)
#         self.txt.setText("no config loaded")
#         self.txt.textChanged.connect(self.txt_changed)
#
#
#     def tab_changed(self, tab_indx):
#         if self.config_tabs.tabText(tab_indx) == 'Advanced':
#             self._temp_conf.update(self.apply(update=False))
#             self.txt.setText(yaml.dump(self._temp_conf))
#
#     def update_config(self, config):
#         """
#         Updates gui values according to input. And stores input in _config and _temp_conf
#         :param config: Dictionary with the new values
#         :type config: dict
#         """
#         self.camera_model.setText(config['camera']['model'])
#         self.camera_init.setText(str(config['camera']['init']))
#         self.camera_camera_model.setText(config['camera']['model_camera'])
#         self.camera_exposure_time.setText(config['camera']['exposure_time'])
#         self.camera_binning_x.setText(str(config['camera']['binning_x']))
#         self.camera_binning_y.setText(str(config['camera']['binning_y']))
#         self.camera_roi_x1.setText(str(config['camera']['roi_x1']))
#         self.camera_roi_x2.setText(str(config['camera']['roi_x2']))
#         self.camera_roi_y1.setText(str(config['camera']['roi_y1']))
#         self.camera_roi_y2.setText(str(config['camera']['roi_y2']))
#         self.camera_background.setText(config['camera']['background'])
#
#         self.saving_directory.setText(config['saving']['directory'])
#         self.saving_filename_photo.setText(config['saving']['filename_photo'])
#         self.saving_filename_video.setText(config['saving']['filename_video'])
#         self.saving_filename_tracks.setText(config['saving']['filename_tracks'])
#         self.saving_filename_log.setText(config['saving']['filename_log'])
#         self.saving_max_memory.setText(str(config['saving']['max_memory']))
#
#         self.other_user_name.setText(config['user']['name'])
#         self.gui_refresh_time.setText(str(config['GUI']['refresh_time']))
#
#         self.logging_level.setCurrentIndex(self.logging_levels[config['debug']['logging_level']])
#         self._config = config
#         self._temp_conf = self._config.copy()
#
#     def apply(self, button_state=None, update=True):
#         """Connected to Apply button.
#         Puts values from gui into config dict"""
#         config = dict(
#             camera=dict(
#                 model=self.camera_model.text(),
#                 init=self.camera_init.text(),
#                 model_camera=self.camera_camera_model.text(),
#                 exposure_time=self.camera_exposure_time.text(),
#                 binning_x=self.camera_binning_x.text(),
#                 binning_y=self.camera_binning_y.text(),
#                 roi_x1=int(self.camera_roi_x1.text()),
#                 roi_x2=int(self.camera_roi_x2.text()),
#                 roi_y1=int(self.camera_roi_y1.text()),
#                 roi_y2=int(self.camera_roi_y2.text()),
#                 background=self.camera_background.text()
#             ),
#             saving=dict(
#                 directory=self.saving_directory.text(),
#                 filename_photo=self.saving_filename_photo.text(),
#                 filename_video=self.saving_filename_video.text(),
#                 filename_tracks=self.saving_filename_tracks.text(),
#                 filename_log=self.saving_filename_log.text(),
#                 max_memory=int(self.saving_max_memory.text())
#             ),
#             user=dict(
#                 name=self.other_user_name.text()
#             ),
#             GUI=dict(
#                 refresh_time=int(self.gui_refresh_time.text())
#             ),
#             debug=dict(
#                 logging_level=self.levels_logging[self.logging_level.currentIndex()]
#             )
#         )
#         if update:
#             if self.config_tabs.tabText(self.config_tabs.currentIndex()) == 'Advanced':
#                 if self.valid_yaml(quiet=False):
#                     # When on the Advanced tab, the values there will overwrite those from the other tabs
#                     config.update(self._temp_conf)
#             else:
#                 # When on the other tabs, those values will overwrite those of the Advanced tab
#                 self._temp_conf.update(config)
#                 config = self._temp_conf
#
#             # if update:
#         #     if self.valid_yaml(quiet=False):
#         #         if self.config_tabs.tabText(self.config_tabs.currentIndex()) == 'Advanced':
#         #             # When on the Advanced tab, the values there will overwrite those from the other tabs
#         #             config.update(self._temp_conf)
#         #         else:
#         #             # When on the other tabs, those values will overwrite those of the Advanced tab
#         #             print('2', type(self._temp_conf))
#         #             self._temp_conf.update(config)
#         #             config = self._temp_conf
#
#             self._config = config
#             self.apply_config.emit(config)
#
#         return config
#
#     def revert_changes(self):
#         """Called by Cancel button"""
#         self.update_config(self._config)
#
#     def txt_changed(self):
#         self.apply_button.setEnabled(self.valid_yaml())
#
#     def valid_yaml(self, quiet=True):
#         """
#         Checks if text in input field can be interpreted as valid yaml.
#         Returns True for valid yaml, False otherwise
#         If optional keyword quiet is set to False it will also display a warning pop-up.
#
#         :param quiet: flag to suppress the warning pop-up (default: True)
#         :type quiet: bool
#         :return: yaml validity
#         :rtype: bool
#         """
#         try:
#             self._temp_conf = yaml.safe_load(self.txt.toPlainText())
#             return True
#         except yaml.YAMLError as exc:
#             if not quiet:
#                 QMessageBox.warning(self, 'Invalid YAML', str(exc), QMessageBox.Ok)
#             return False


class ConfigWidget(QWidget):
    """Widget for configuring the main parameters of the camera.
    """
    flags = Qt.WindowStaysOnTopHint
    apply_config = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent, flags=self.flags)
        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'designer', 'config_general.ui'), self)
        self.status_bar = QStatusBar()
        self.layout().addWidget(self.status_bar)

        self.logging_levels = {
            'Nothing': 0,
            'Debug': 1,
            'Info': 2,
            'Warning': 3,
            'Error': 4,
        }

        self.levels_logging = dict(zip(self.logging_levels.values(), self.logging_levels.keys()))

        self.config = None  # this will hold the config of the experiment as last supplied by update_config()
        self._config = {}  # this will hold the "current version" in the config window

        self.apply_button.clicked.connect(self.apply)
        self.cancel_button.clicked.connect(self.revert_changes)

        self.config_tabs.currentChanged.connect(self.tab_changed)
        self.font = QFont("Courier New", 10)


        self.txt.setLineWrapMode(QTextEdit.NoWrap)
        self.txt.setFont(self.font)
        self.txt.setText("no config loaded")
        self.txt.textChanged.connect(self.txt_changed)

    def tab_changed(self, tab_indx):
        if self.config_tabs.tabText(tab_indx) == 'Advanced':
            self.apply_gui_to_local_conf()
            self.txt.setText(yaml.dump(self._config))
        else:
            self.update_gui()

    def update_config(self, conf):
        """Called externally to "load" the config."""
        self.config = conf
        self.revert_changes()  # updates _config and gui elements

    def update_gui(self):
        self.camera_model.setText(self._config['camera']['model'])
        self.camera_init.setText(str(self._config['camera']['init']))
        self.camera_camera_model.setText(self._config['camera']['model_camera'])
        self.camera_exposure_time.setText(self._config['camera']['exposure_time'])
        self.camera_binning_x.setText(str(self._config['camera']['binning_x']))
        self.camera_binning_y.setText(str(self._config['camera']['binning_y']))
        self.camera_roi_x1.setText(str(self._config['camera']['roi_x1']))
        self.camera_roi_x2.setText(str(self._config['camera']['roi_x2']))
        self.camera_roi_y1.setText(str(self._config['camera']['roi_y1']))
        self.camera_roi_y2.setText(str(self._config['camera']['roi_y2']))
        self.camera_background.setText(self._config['camera']['background'])

        self.saving_directory.setText(self._config['saving']['directory'])
        self.saving_filename_photo.setText(self._config['saving']['filename_photo'])
        self.saving_filename_video.setText(self._config['saving']['filename_video'])
        self.saving_filename_tracks.setText(self._config['saving']['filename_tracks'])
        self.saving_filename_log.setText(self._config['saving']['filename_log'])
        self.saving_max_memory.setText(str(self._config['saving']['max_memory']))

        self.other_user_name.setText(self._config['user']['name'])
        self.gui_refresh_time.setText(str(self._config['GUI']['refresh_time']))

        self.logging_level.setCurrentIndex(self.logging_levels[self._config['debug']['logging_level']])

    def apply_gui_to_local_conf(self):
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
        )
        self._config['camera'].update(camera)
        saving=dict(
            directory=self.saving_directory.text(),
            filename_photo=self.saving_filename_photo.text(),
            filename_video=self.saving_filename_video.text(),
            filename_tracks=self.saving_filename_tracks.text(),
            filename_log=self.saving_filename_log.text(),
            max_memory=int(self.saving_max_memory.text())
        )
        self._config['saving'].update(saving)
        user=dict(
            name=self.other_user_name.text()
        )
        self._config['user'].update(user)
        GUI=dict(
            refresh_time=int(self.gui_refresh_time.text())
        )
        self._config['GUI'].update(GUI)
        debug=dict(
            logging_level=self.levels_logging[self.logging_level.currentIndex()]
        )
        self._config['debug'].update(debug)

    # def update_config(self, config):
    #     """
    #     Updates gui values according to input. And stores input in _config and _temp_conf
    #     :param config: Dictionary with the new values
    #     :type config: dict
    #     """
    #     self.camera_model.setText(config['camera']['model'])
    #     self.camera_init.setText(str(config['camera']['init']))
    #     self.camera_camera_model.setText(config['camera']['model_camera'])
    #     self.camera_exposure_time.setText(config['camera']['exposure_time'])
    #     self.camera_binning_x.setText(str(config['camera']['binning_x']))
    #     self.camera_binning_y.setText(str(config['camera']['binning_y']))
    #     self.camera_roi_x1.setText(str(config['camera']['roi_x1']))
    #     self.camera_roi_x2.setText(str(config['camera']['roi_x2']))
    #     self.camera_roi_y1.setText(str(config['camera']['roi_y1']))
    #     self.camera_roi_y2.setText(str(config['camera']['roi_y2']))
    #     self.camera_background.setText(config['camera']['background'])
    #
    #     self.saving_directory.setText(config['saving']['directory'])
    #     self.saving_filename_photo.setText(config['saving']['filename_photo'])
    #     self.saving_filename_video.setText(config['saving']['filename_video'])
    #     self.saving_filename_tracks.setText(config['saving']['filename_tracks'])
    #     self.saving_filename_log.setText(config['saving']['filename_log'])
    #     self.saving_max_memory.setText(str(config['saving']['max_memory']))
    #
    #     self.other_user_name.setText(config['user']['name'])
    #     self.gui_refresh_time.setText(str(config['GUI']['refresh_time']))
    #
    #     self.logging_level.setCurrentIndex(self.logging_levels[config['debug']['logging_level']])
    #     self._config = config
    #     self._temp_conf = self._config.copy()

    def apply(self):
        self.config = self._config
        self.apply_config.emit(self.config)
        self.close()

    # def apply(self, button_state=None, update=True):
    #     """Connected to Apply button.
    #     Puts values from gui into config dict"""
    #     config = dict(
    #         camera=dict(
    #             model=self.camera_model.text(),
    #             init=self.camera_init.text(),
    #             model_camera=self.camera_camera_model.text(),
    #             exposure_time=self.camera_exposure_time.text(),
    #             binning_x=self.camera_binning_x.text(),
    #             binning_y=self.camera_binning_y.text(),
    #             roi_x1=int(self.camera_roi_x1.text()),
    #             roi_x2=int(self.camera_roi_x2.text()),
    #             roi_y1=int(self.camera_roi_y1.text()),
    #             roi_y2=int(self.camera_roi_y2.text()),
    #             background=self.camera_background.text()
    #         ),
    #         saving=dict(
    #             directory=self.saving_directory.text(),
    #             filename_photo=self.saving_filename_photo.text(),
    #             filename_video=self.saving_filename_video.text(),
    #             filename_tracks=self.saving_filename_tracks.text(),
    #             filename_log=self.saving_filename_log.text(),
    #             max_memory=int(self.saving_max_memory.text())
    #         ),
    #         user=dict(
    #             name=self.other_user_name.text()
    #         ),
    #         GUI=dict(
    #             refresh_time=int(self.gui_refresh_time.text())
    #         ),
    #         debug=dict(
    #             logging_level=self.levels_logging[self.logging_level.currentIndex()]
    #         )
    #     )
    #     if update:
    #         if self.config_tabs.tabText(self.config_tabs.currentIndex()) == 'Advanced':
    #             if self.valid_yaml(quiet=False):
    #                 # When on the Advanced tab, the values there will overwrite those from the other tabs
    #                 config.update(self._temp_conf)
    #         else:
    #             # When on the other tabs, those values will overwrite those of the Advanced tab
    #             self._temp_conf.update(config)
    #             config = self._temp_conf
    #
    #         # if update:
    #     #     if self.valid_yaml(quiet=False):
    #     #         if self.config_tabs.tabText(self.config_tabs.currentIndex()) == 'Advanced':
    #     #             # When on the Advanced tab, the values there will overwrite those from the other tabs
    #     #             config.update(self._temp_conf)
    #     #         else:
    #     #             # When on the other tabs, those values will overwrite those of the Advanced tab
    #     #             print('2', type(self._temp_conf))
    #     #             self._temp_conf.update(config)
    #     #             config = self._temp_conf
    #
    #         self._config = config
    #         self.apply_config.emit(config)
    #
    #     return config

    def revert_changes(self):
        """Called by Cancel button"""
        self._config = self.config.copy()
        self.txt.setText(yaml.dump(self._config))
        self.update_gui()

    def txt_changed(self):
        valid = self.valid_yaml()
        self.config_tabs.setTabEnabled(0, valid)
        self.config_tabs.setTabEnabled(1, valid)
        self.config_tabs.setTabEnabled(2, valid)
        self.apply_button.setEnabled(valid)

    def valid_yaml(self, quiet=False):
        """
        Checks if text in input field can be interpreted as valid yaml.
        Returns True for valid yaml, False otherwise
        If optional keyword quiet is set to False it will also display a warning pop-up.

        :param quiet: flag to suppress the warning pop-up (default: True)
        :type quiet: bool
        :return: yaml validity
        :rtype: bool
        """
        try:
            self._config = yaml.safe_load(self.txt.toPlainText())
            self.status_bar.showMessage('YAML Ok')
            return True
        except yaml.YAMLError as exc:
            if not quiet:
                self.status_bar.showMessage('Invalid YAML: ' + str(exc))
                # QMessageBox.warning(self, 'Invalid YAML', str(exc), QMessageBox.Ok)
            return False
