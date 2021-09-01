import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QPushButton
from numpy import square

from pynta.view.GUI.histogram_widget import HistogramWidget
from pynta.view.GUI.tracks_widget import TracksWidget
from pynta.view.GUI.graph_monitor_widget import GraphMonitorWidget
from pyqtgraph.dockarea import DockArea, Dock
from pynta.util.log import get_logger

from pynta.model.daqs.signal_generator.base_signal_generator import BaseSignalGenerator, Waveform
#todo: support different waveform, standardize initialization.
#
class SignalGeneratorWidget(QWidget):
    #init takes a parent argument which has to be another QWidget or None, and the model
    def __init__(self, parent=None):
        # call the base QWidget class initializer
        super().__init__(parent)
        #load the corresponding UI file.
        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'designer', 'signal_generator.ui'), self)
        self.logger = get_logger(name=__name__)
        self.model = None
        self.connectSignals()
    
    def set_model(self, model : BaseSignalGenerator):
        self.model = model
        (min_f, max_f) = model.supported_frequencies().get_range()
        self.FrequencySpinbox.setRange(min_f, max_f)
        self.FrequencySpinbox.setValue(0.5*(min_f+max_f))
        (min_a, max_a) = model.supported_amplitudes().get_range()
        self.AmplitudeSpinbox.setRange(min_a, max_a)
        self.AmplitudeSpinbox.setValue(0.5*(min_a+max_a))
        (min_o, max_o) = model.supported_offsets().get_range()
        self.OffsetSpinbox.setRange(min_o, max_o)
        self.OffsetSpinbox.setValue(0.5*(min_o+max_o))
        for waveform in model.supported_waveforms():
            self.WaveformSelector.addItem(waveform.name, waveform)
        print("Supports live updates?", model.supports_live_updates())
        # self.flush_settings()
        self.set_waveform()

    def connectSignals(self):
        self.WaveformSelector.currentTextChanged.connect(self.set_waveform)
        self.UpdateButton.clicked.connect(self.flush_settings)
    
    
    def set_waveform(self):
         self.DutyCycleSpinbox.setEnabled(self.WaveformSelector.currentData() == Waveform.Square)

    def flush_settings(self):
        if self.model is None:
            raise ValueError("Can't flush signal generator settings without first setting a model!")
        waveform = self.WaveformSelector.currentData()
        if waveform == Waveform.Sine:
            self.model.set_sine_wave(self.FrequencySpinbox.value(), self.AmplitudeSpinbox.value(), self.OffsetSpinbox.value())
        elif waveform == Waveform.Square:
            self.model.set_square_wave(self.FrequencySpinbox.value(), self.AmplitudeSpinbox.value(), self.OffsetSpinbox.value(), self.DutyCycleSpinbox.value())
        else:
            raise ValueError('Invalid Waveform {} passed to model {}'.format(waveform, self.model))
        #self.model.flush()
