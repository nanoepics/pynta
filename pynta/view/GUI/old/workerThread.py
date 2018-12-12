"""
    UUTrack.View.Camera.workerThread
    ================================

    Thread that acquires continuously data until a variable is changed. This enables to acquire at any frame rate without freezing the GUI or overloading it with data being acquired too fast.

"""

from pyqtgraph.Qt import QtCore


class workThread(QtCore.QThread):
    """Thread for acquiring from the camera. If the exposure time is long, this is
    needed to avoid freezing the GUI.
    """
    def __init__(self,_session,camera):
        QtCore.QThread.__init__(self)
        self._session = _session
        self.camera = camera
        self.origin = None
        self.keep_acquiring = True

    def __del__(self):
        self.wait()

    def run(self):
        """ Triggers the Monitor to acquire a new Image.
        the QThread defined .start() method is a special method that sets up the thread and
        calls our implementation of the run() method.
        """
        first = True
        while self.keep_acquiring:
            if self.origin == 'snap':
                self.keep_acquiring = False
            if first:
                self.camera.setAcquisitionMode(self.camera.MODE_CONTINUOUS)
                self.camera.triggerCamera()  # Triggers the camera only once
                first = False
            img = self.camera.readCamera()
            
            self.emit(QtCore.SIGNAL('image'), img, self.origin)
        self.camera.stopAcq()
        return
