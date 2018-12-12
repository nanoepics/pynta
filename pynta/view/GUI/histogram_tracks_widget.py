import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

from pynta.view.GUI.histogram_widget import HistogramWidget
from pynta.view.GUI.tracks_widget import TracksWidget


class HistogramTracksWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'designer', 'histogram_tracks.ui'), self)

        self.histogram_widget = HistogramWidget(self)
        self.tracks_widget = TracksWidget(self)

        self.tabWidget.addTab(self.histogram_widget, 'Histogram')
        self.tabWidget.addTab(self.tracks_widget, 'Trajectories')
