"""
    UUTrack.View.Camera.cameraViewer.py
    ===================================
    Independent window for viewing the camera. It is useful since it allows to quickly check the full CCD without changing the parameters of the main window. 
    It could have been design in such a way that can be run independently, for fast visualization without the need of controlling.
    
    .. todo:: The viewer should inherit from :mod:`UUTrack.Viewer.Camera.cameraMainWidget` in order to have the same interface and not replicate code.
    
    .. todo:: Unify the main viewer with this one.
    
    .. sectionauthor:: Aquiles Carattino <aquiles@aquicarattino.com>
"""

import pyqtgraph as pg
from pyqtgraph import GraphicsLayoutWidget
from pyqtgraph.Qt import QtGui, QtCore

from pynta.view.GUI.old.workerThread import workThread


class cameraViewer(QtGui.QMainWindow):
    """Main window for the viewer.
    """
    def __init__(self,session,camera,parent=None):
        super(cameraViewer,self).__init__()

        self._session = session
        self.camera = camera
        self.parent = parent
        self.setWindowTitle('On-Demand Camera Terminal')
        self.viewerWidget = viewerWidget()
        self.setCentralWidget(self.viewerWidget)

        QtCore.QObject.connect(self.viewerWidget.startButton,QtCore.SIGNAL('clicked()'),self.startCamera)
        QtCore.QObject.connect(self.viewerWidget.stopButton,QtCore.SIGNAL('clicked()'),self.startCamera)
        self.acquiring = False

        self.tempImage = []

        self.refreshTimer = QtCore.QTimer()
        self.refreshTimer.start(self._session.GUI['refresh_time']) # In milliseconds

        self.connect(self.refreshTimer,QtCore.SIGNAL("timeout()"),self.updateGUI)


    def startCamera(self):
        """Starts a continuous acquisition of the camera.
        """
        self.emit(QtCore.SIGNAL('stopMainAcquisition'))
        if self.acquiring:
            self.stopCamera()
        else:
            self.acquiring = True
            self.workerThread = workThread(self._session,self.camera)
            self.connect(self.workerThread,QtCore.SIGNAL('image'),self.getData)
            self.workerThread.start()

    def stopCamera(self):
        """Stops the acquisition.
        """
        if self.acquiring:
            self.workerThread.keep_acquiring = False
            self.acquiring = False

    def getData(self,data,origin):
        """Gets the data that is being gathered by the working thread.
        """
        self.tempImage = data

    def updateGUI(self):
        """Updates the GUI at regular intervals.
        """
        if len(self.tempImage) >= 1:
            self.viewerWidget.img.setImage(self.tempImage)

    def closeViewer(self):
        """What to do when the viewer is triggered to close from outside.
        """
        self.stopCamera()
        self.close()

    def closeEvent(self,evnt):
        """Triggered at closing. If it is running as main window or not.
        """
        if self.parent == None:
            self.emit(QtCore.SIGNAL('closeAll'))
            self.camera.stopCamera()
            self.workerThread.terminate()
            self.close()
        else:
            self.closeViewer()

class viewerWidget(QtGui.QWidget):
    """Widget for holding the GUI elements of the viewer.
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.layout = QtGui.QVBoxLayout(self)

        self.viewport = GraphicsLayoutWidget()
        self.view = self.viewport.addViewBox(enableMenu=True)
        self.img = pg.ImageItem()
        self.view.addItem(self.img)

        self.buttons = QtGui.QHBoxLayout()
        self.startButton = QtGui.QPushButton('Start')
        self.stopButton = QtGui.QPushButton('Stop')
        self.buttons.addWidget(self.startButton)
        self.buttons.addWidget(self.stopButton)

        self.setLayout(self.layout)
        self.layout.addWidget(self.viewport)
        self.layout.addLayout(self.buttons)
