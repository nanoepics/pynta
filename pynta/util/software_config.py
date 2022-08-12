# If you want to use the NI daq import NiUsb6216 instead of DummyNiUsb6216
from pynta.controller.NIDAQ.ni_usb_6216 import DummyNiUsb6216 as DaqController

# If you add a new experiment, change this import such that it will be used when starting pynta
from pynta.model.experiment.example import Experiment

# If you add a new GUI, change this import such that it will be used when starting pynta
from pynta.view.dcam_main_view import MainWindow
