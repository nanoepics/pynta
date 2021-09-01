import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QPushButton

from pynta.view.GUI.histogram_widget import HistogramWidget
from pynta.view.GUI.tracks_widget import TracksWidget
from pynta.view.GUI.graph_monitor_widget import GraphMonitorWidget
from pyqtgraph.dockarea import DockArea, Dock

class AnalysisDockWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'designer', 'analysis_dock.ui'), self)

        self.histogram_widget = HistogramWidget(self)
        self.tracks_widget = TracksWidget(self)
        self.intensities_widget = GraphMonitorWidget(self)

        self.dockarea = DockArea()
        self.layout().insertWidget(0, self.dockarea)

        self.histogram_dock = Dock(name='Histogram', closable=False)
        self.histogram_dock.addWidget(self.histogram_widget)
        self.dockarea.addDock(self.histogram_dock)

        self.tracks_dock = Dock(name='Trajectories', closable=False)
        self.tracks_dock.addWidget(self.tracks_widget)
        self.dockarea.addDock(self.tracks_dock)

        self.intensities_dock = Dock(name='Intensities', closable=False)
        self.intensities_dock.addWidget(self.intensities_widget)
        self.dockarea.addDock(self.intensities_dock)
