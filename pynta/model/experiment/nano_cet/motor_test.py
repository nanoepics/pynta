import importlib

from pynta.model.experiment.base_experiment import BaseExperiment
from pynta.model.motors.arduino_base import Arduino


class MotorTestExperiment(BaseExperiment):
    def __init__(self, filename=None):
        super().__init__()
        self.load_configuration(filename)
        self.arduino = None

    def initialize_camera(self):
        try:
            self.logger.info('Importing camera model {}'.format(self.config['camera']['model']))
            self.logger.debug('pynta.model.cameras.' + self.config['camera']['model'])

            camera_model_to_import = 'pynta.model.cameras.' + self.config['camera']['model']
            cam_module = importlib.import_module(camera_model_to_import)
        except ModuleNotFoundError:
            self.logger.error('The model {} for the camera was not found'.format(self.config['camera']['model']))
            raise
        except:
            self.logger.exception('Unhandled exception')
            raise

        cam_init_arguments = self.config['camera']['init']
        if 'extra_args' in self.config['camera']:
            self.logger.info('Initializing camera with extra arguments')
            self.logger.debug('cam_module.camera({}, {})'.format(cam_init_arguments, self.config['camera']['extra_args']))
            self.camera = cam_module.camera(cam_init_arguments, *self.config['Camera']['extra_args'])
        else:
            self.logger.info('Initializing camera without extra arguments')
            self.logger.debug('cam_module.camera({})'.format(cam_init_arguments))
            self.camera = cam_module.camera(cam_init_arguments)
            self.current_width, self.current_height = self.camera.getSize()
            self.logger.info('Camera sensor ROI: {}px X {}px'.format(self.current_width, self.current_height))
            self.max_width = self.camera.GetCCDWidth()
            self.max_height = self.camera.GetCCDHeight()
            self.logger.info('Camera sensor size: {}px X {}px'.format(self.max_width, self.max_height))

        self.camera.initialize()

    def initialize_arduino(self):
        self.arduino = Arduino(self.config['arduino']['port'])

    def motor_right(self):
        self.arduino.move_motor(1, 1)

    def motor_left(self):
        self.arduino.move_motor(1, 0)

    def motor_top(self):
        self.arduino.move_motor(2, 1)

    def motor_bottom(self):
        self.arduino.move_motor(2, 0)