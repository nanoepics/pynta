"""
    Nano CET exceptions
    ===================
    Collection of custom exceptions for the nanoCET experiment.

"""


class CameraNotInitialized(Exception):
    pass

class StreamSavingRunning(Exception):
    pass