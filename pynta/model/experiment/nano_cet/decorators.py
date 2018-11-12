"""
    Nano CET decorators
    ===================

    Useful decorators for the Nano CET experiment.
    For example, to check whether the camera was initialized already or not before calling a method that needs an active
    camera.

"""
import warnings
from functools import wraps

from pynta.model.experiment.nano_cet.exceptions import CameraNotInitialized


def check_camera(func):
    """Decorator to check whether the camera has been already initialized.
    It raises an error if it has not been."""
    @wraps(func)
    def func_wrapper(cls, *args, **kwargs):
        if hasattr(cls, 'camera'):
            if cls.camera is not None:
                return func(cls, *args, **kwargs)

        if hasattr(cls, 'logger'):
            cls.logger.error('Trying to run {} before initializing a camera'.format(func.__name__))

        raise CameraNotInitialized('At least one camera has to be initialized before calling {}'.format(func.__name__))

    return func_wrapper

def check_not_acquiring(func):
    """Decorator to check that the camera is not acquiring before running the function. This prevents, for example,
    changing the ROI while a movie is in progress.
    This decorator works in conjuction with ``check_camera``, i.e., it will not double check whether the camera was
    initialized or not.

    """
    @wraps(func)
    def func_wrapper(cls, *args, **kwargs):
        if cls.camera.running:
            warnings.warn('Trying to run {} while the camera is still running'.format(func.__name__))
            return

        return func(cls, *args, **kwargs)

    return func_wrapper