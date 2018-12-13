__version__ = '0.1.1'

from pint import UnitRegistry
from multiprocessing import Event

ureg = UnitRegistry()
Q_ = ureg.Quantity

general_stop_event = Event()  # This event is the last resource to stop threads and processes