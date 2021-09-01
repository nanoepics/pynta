"""
    Nano CET exceptions
    ===================
    Collection of custom exceptions for the nanoCET experiment.

"""

class NanoCETException(Exception):
    pass

class CameraNotInitialized(NanoCETException):
    pass

class StreamSavingRunning(NanoCETException):
    pass

class TrackpyNotInstalled(NanoCETException):
    pass

class DiameterNotDefined(NanoCETException):
    pass

class LinkException(NanoCETException):
    pass