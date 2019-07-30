import importlib

from pynta.util import get_logger

logger = get_logger(name=__name__)


def load_camera_module(name):
    try:
        logger.info('Importing camera model {}'.format(name))
        logger.debug('pynta.model.cameras.' + name)
        camera_model_to_import = 'pynta.model.cameras.' + name
        cam_module = importlib.import_module(camera_model_to_import)
    except ModuleNotFoundError:
        logger.error('The model {} for the camera was not found'.format(name))
        raise
    return cam_module


def instantiate_camera(config: dict):
    cam_module = load_camera_module(config['model'])
    cam_init_arguments = config['init']
    if 'extra_args' in config:
        logger.info('Initializing camera with extra arguments')
        logger.debug('cam_module.camera({}, {})'.format(cam_init_arguments, config['extra_args']))
        camera = cam_module.Camera(cam_init_arguments, *config['extra_args'])
    else:
        logger.info('Initializing camera without extra arguments')
        logger.debug('cam_module.camera({})'.format(cam_init_arguments))
        camera = cam_module.Camera(cam_init_arguments)

    return camera
