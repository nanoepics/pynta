import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QPushButton
import numpy as np

from pyqtgraph.dockarea import DockArea, Dock
#todo: abstract into generic model
#from pynta.controller.devices.NIDAQ.ni_usb_6216 import NiUsb6216 as Adc
from pynta.util.log import get_logger

class AdcCaptureWidget(QWidget):
    #init takes a parent argument which has to be another QWidget or None, and the model
    def __init__(self, parent=None):
        # set the base variables
        self.model = None
        # call the base QWidget class initializer
        super().__init__(parent)
        #load the corresponding UI file.
        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'designer', 'adc.ui'), self)
        #(min_f, max_f) = model.supported_frequencies().get_range()
        self.FrequencySpinbox.setRange(1e2, 5e3)
        self.FrequencySpinbox.setValue(1e3)
        #(min_a, max_a) = model.supported_amplitudes().get_range()
        self.PointsSpinbox.setRange(100, 10000)
        self.PointsSpinbox.setValue(2000)
        self.curve = self.PlotView.plot(np.zeros(1000))
        self.connectSignals()
    
    def set_model(self, model):
        self.model = model
        model.set_display_function(self.set_display_data)
    
    def add_to_aqcuisition(self, aqc):
        pass

    def connectSignals(self):
        self.UpdateButton.clicked.connect(self.flush_settings)

    def set_display_data(self, data):
        self.curve.setData(data)

    def flush_settings(self):
        #should_view = self.ViewData.isChecked()
        #should_save = self.ShouldSave.isChecked()
        if self.model is None:
            get_logger(name=__name__).error("No model set, can't start capture signal!")
            return
        self.model.capture_stream(self.FrequencySpinbox.value(), self.PointsSpinbox.value())
