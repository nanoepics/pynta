from pynta.model.exceptions import ModelException

class CameraException(ModelException):
    pass

class CameraNotFound(CameraException):
    pass

class WrongCameraState(CameraException):
    pass