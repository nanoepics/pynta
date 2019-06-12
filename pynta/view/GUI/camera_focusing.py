import os
import pyqtgraph as pg

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QAction
from pyqtgraph import GraphicsLayoutWidget

from pynta.view.GUI.camera_viewer_widget import CameraViewerWidget

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class CameraFocusing(QMainWindow):
    def __init__(self, experiment=None, parent=None):
        super(CameraFocusing, self).__init__(parent)
        uic.loadUi(os.path.join(BASE_DIR, 'designer/focusing_window.ui'), self)
        self.experiment = experiment

        self.camera_viewer = CameraViewerWidget(self)
        self.layout = self.camera_widget.layout()
        self.layout.addWidget(self.camera_viewer)

        self.button_right.clicked.connect(self.experiment.motor_right)
        self.button_left.clicked.connect(self.experiment.motor_left)
        self.button_up.clicked.connect(self.experiment.motor_top)
        self.button_down.clicked.connect(self.experiment.motor_bottom)




if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    win = CameraFocusing()
    win.show()
    app.exit(app.exec())