"""
Equivalent of view GUI main_window.py modified
"""

import os

# from pyqtgraph.dockarea.DockArea import DockArea

# from pynta.model.daqs.signal_generator.dummy_signal_generator import DummySignalGenerator


# from pynta.controller.devices.NIDAQ.ni_usb_6216 import NiUsb6216

from PyQt5 import uic
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QPushButton, QSplitter, QComboBox
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import numpy as np
# This is what allows the icons to show up even if not explicitly used in the code
from pynta.view.GUI import resources
from pynta.util.log import get_logger
from pynta.view.GUI.camera_viewer_widget import CameraViewerWidget
# from pynta.view.GUI.config_tracking_widget import ConfigTrackingWidget
from pynta.view.GUI.config_widget import ConfigWidget
# from pynta.view.GUI.analysis_dock_widget import AnalysisDockWidget
from pynta.view.GUI.signal_generator_widget import SignalGeneratorWidget
from pynta.view.GUI.adc_capture_widget import AdcCaptureWidget
import logging
import time
# from pynta.model.daqs.signal_generator.stm_signal_generator import StmSignalGenerator


class MainWindowGUI(QMainWindow):
    def __init__(self, refresh_time=30):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(
            __file__)), 'designer', 'MainWindow.ui'), self)
        self.logger = get_logger(name=__name__)

        # class LogInStatusBar(logging.Handler):
        #     def __init__(self, statusbar, parent):
        #         super().__init__()
        #         self.bar = statusbar
        #
        #     def emit(self, record):
        #         msg = '{:<7} {}    [{}: {}: {}] ({})'.format(record.levelname + ': ', record.msg, record.module,
        #                                                      record.lineno, record.funcName, record.name)
        #         duration = record.levelno * 300 if record.levelno < 40 else 0
        #         self.bar.showMessage(msg, duration)

        # root_logger = logging.getLogger()
        # root_logger.addHandler(LogInStatusBar(self.statusBar, self))

        self.central_layout = QHBoxLayout(self.centralwidget)
        self.widget_splitter = QSplitter()

        self.camera_viewer_widget = CameraViewerWidget(self)
        #self.analysis_dock_widget = AnalysisDockWidget(self)
        self.daq_splitter = QSplitter(orientation = Qt.Vertical)

        self.signal_gen_widget = SignalGeneratorWidget(self)

        self.plot_widget = AdcCaptureWidget(self)
        self.daq_splitter.addWidget(self.signal_gen_widget)
        self.daq_splitter.addWidget(self.plot_widget)

        self.widget_splitter.addWidget(self.camera_viewer_widget)
        #self.widget_splitter.addWidget(self.analysis_dock_widget)

        self.widget_splitter.addWidget(self.daq_splitter)

        self.widget_splitter.setSizes((750, 500))
        self.central_layout.addWidget(self.widget_splitter)

        self.config_widget = ConfigWidget()
        # self.config_tracking_widget = ConfigTrackingWidget()

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_gui)
        self.refresh_timer.start(refresh_time)

        self.showMaximized()

        self.connect_actions()
        self.connect_buttons()
        self.connect_signals()
        self.addMeasurementSelector()

        self.statusBar.clearMessage()

        self.actionStop_Tracking.setEnabled(False)
        self.actionStart_Tracking.setEnabled(False)
        self.actionStop_Linking.setEnabled(False)
        self.actionStart_Linking.setEnabled(False)


    def addMeasurementSelector(self):
        """ Adds the GUI elements to run measurement methods """
        self.measurement_combo = QComboBox()
        self.toolBar.addWidget(self.measurement_combo)
        self.measurement_run = QPushButton('Run')
        self.toolBar.addWidget(self.measurement_run)

    def update_gui(self):
        self.logger.error('Update gui not defined')

    def connect_signals(self):
        # self.config_tracking_widget.apply_config.connect(
        #     self.update_tracking_config)
        self.config_widget.apply_config.connect(self.update_config)

    def connect_buttons(self):
        # self.analysis_dock_widget.button_histogram.clicked.connect(
        #     self.calculate_histogram)
        # self.analysis_dock_widget.button_tracks.clicked.connect(
        #     self.update_tracks)
        pass

    def connect_actions(self):
        self.actionClose.triggered.connect(self.safe_close)
        self.actionLoad_Config.triggered.connect(self.load_config)
        self.actionSave_Image.triggered.connect(self.save_image)
        self.actionLoad_Data.triggered.connect(self.load_data)
        self.actionSnap_Photo.triggered.connect(self.snap)
        self.actionStart_Movie.triggered.connect(self.toggle_movie)
        self.actionStop_Movie.triggered.connect(self.toggle_movie)
        self.actionStart_Continuous_Saves.triggered.connect(
            self.toggle_saving)
        self.actionStop_Continuous_Saves.triggered.connect(
            self.toggle_saving)
        self.actionSet_ROI.triggered.connect(self.set_roi)
        self.actionClear_ROI.triggered.connect(self.clear_roi)
        self.actionConfiguration.triggered.connect(self.configure)
        self.actionToggle_bg_reduction.triggered.connect(
            self.toggle_background)
        self.actionStart_Tracking.triggered.connect(self.start_tracking)
        self.actionStop_Tracking.triggered.connect(self.stop_tracking)
        self.actionStart_Linking.triggered.connect(self.start_linking)
        self.actionStop_Linking.triggered.connect(self.stop_linking)
        self.actionSave_Tracks.triggered.connect(self.start_saving_tracks)
        self.actionShow_Cheatsheet.triggered.connect(self.show_cheat_sheet)
        self.actionAbout.triggered.connect(self.show_about)
        self.actionInitialize_Camera.triggered.connect(self.initialize_camera)
        self.actionUpdate_Histogram.triggered.connect(self.calculate_histogram)
        # self.actionTracking_Config.triggered.connect(self.config_tracking_widget.show)
        self.actionConfiguration.triggered.connect(self.config_widget.show)
        self.actionAdd_Monitor_Point.triggered.connect(self.add_monitor_point)
        self.actionClear_All.triggered.connect(self.clear_monitor_points)
        self.actionZoom.triggered.connect(self.zoom_ROI_prime)
        self.actionToggleLiveImageProcessing.triggered.connect(self.toggle_live_img_process)

    def toggle_live_img_process(self):
        self.logger.warnings('live_img_process method not implemented in child class')

    def zoom_ROI_prime(self):
        self.logger.warnings('Zoom ROI method not implemented in child class')

    def add_monitor_point(self):
        self.logger.debug('Add monitor point')

    def clear_monitor_points(self):
        self.logger.debug('Clear all monitor points')

    def initialize_camera(self):
        self.logger.debug('Initialize Camera')

    def show_about(self):
        self.logger.debug('Showing About')

    def load_config(self):
        self.logger.debug('Loading config')

    def snap(self):
        self.logger.debug('Snapped a photo')

    def save_image(self):
        self.logger.debug('Saved an image')

    def toggle_movie(self):
        self.logger.warning('Toggle movie method not implemented in child class')

    def toggle_saving(self):
        self.logger.warning('Toggle saving method not implemented in child class')

    def start_tracking(self):
        self.logger.debug('Started tracking particles')

    def stop_tracking(self):
        self.logger.debug('Stopped tracking particles')

    def start_saving_tracks(self):
        self.logger.debug('Started saving tracks')

    def stop_saving_tracks(self):
        self.logger.debug('Stopped saving tracks')

    def start_linking(self):
        self.logger.debug('Started linking particles')

    def stop_linking(self):
        self.logger.debug('Stopped linking')

    def configure(self):
        self.logger.debug('Showed the config window')

    def set_roi(self):
        self.logger.debug('Setting the ROI')

    def clear_roi(self):
        self.logger.debug('Resetting the ROI')

    def background_reduction(self):
        self.logger.debug('Setting background reduction')

    def show_cheat_sheet(self):
        self.logger.debug('Showing the cheat sheet')

    def load_data(self):
        self.logger.debug('Loading data')

    def safe_close(self):
        self.logger.debug('Closing the program')
        self.close()

    def calculate_histogram(self):
        self.logger.error('Update Histogram method not defiend')

    def update_tracks(self):
        self.logger.error('Update tracks method not defined')

    def update_tracking_config(self, config):
        self.logger.error('Update Tracking config method not defined')

    def update_config(self, config):
        # print('actually update config')
        self.logger.error('Update Config method not defined')

    def closeEvent(self, *args, **kwargs):
        self.config_widget.close()
        # self.config_tracking_widget.close()
        super(MainWindowGUI, self).closeEvent(*args, **kwargs)


if __name__ == "__main__":
    import sys
    import logging
    from PyQt5.QtWidgets import QApplication

    logger = get_logger(name=__name__)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    app = QApplication([])
    win = MainWindowGUI()
    win.show()
    sys.exit(app.exec_())
