from pynta.model.experiment.base_experiment import BaseExperiment
from pynta.model.motors.arduino_base import Arduino


class MotorTestExperiment(BaseExperiment):
    def __init__(self, filename=None):
        super().__init__()
        self.load_configuration(filename)
        self.arduino = None

    def initialize_arduino(self):
        self.arduino = Arduino(self.config['arduino']['port'])

    def motor_right(self):
        self.arduino.set_speed(1, 1, 50)
        self.arduino.set_speed(1, 1, 0)

    def motor_left(self):
        self.arduino.set_speed(1, 0, 50)
        self.arduino.set_speed(1, 0, 0)

    def motor_top(self):
        self.arduino.set_speed(2, 1, 50)
        self.arduino.set_speed(2, 1, 0)

    def motor_bottom(self):
        self.arduino.set_speed(2, 0, 50)
        self.arduino.set_speed(2, 0, 0)
