import pyqtgraph as pg
import numpy as np

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QAction
from pyqtgraph import GraphicsLayoutWidget


class CameraViewerWidget(QWidget):
    """Widget for holding the images generated by the camera.
    """
    specialTask = pyqtSignal()
    stopSpecialTask = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # General layout of the widget to hold an image and a histogram
        self.layout = QHBoxLayout(self)

        # Settings for the image
        self.viewport = GraphicsLayoutWidget()
        self.view = self.viewport.addViewBox(lockAspect=False, enableMenu=True)

        self.autoScale = QAction("Auto Range", self.view.menu)
        self.autoScale.triggered.connect(self.do_auto_scale)
        self.view.menu.addAction(self.autoScale)

        self.img = pg.ImageItem()
        self.marker = pg.PlotDataItem(pen=None)
        self.marker.setBrush(255, 0, 0, 255)
        self.view.addItem(self.img)
        self.view.addItem(self.marker)
        self.imv = pg.ImageView(view=self.view, imageItem=self.img)

        # Add everything to the widget
        self.layout.addWidget(self.imv)
        self.setLayout(self.layout)

        self.showCrosshair = False
        self.showCrossCut = False
        self.rois = []
        self.radius_circle = 10 # The radius to draw around particles

        self.corner_roi = [0, 0]  # Initial ROI corner for the camera

        self.first_image = True

    def setup_roi_lines(self, max_size):
        """Sets up the ROI lines surrounding the image.

        :param list max_size: List containing the maximum size of the image to avoid ROIs bigger than the CCD."""

        self.hline1 = pg.InfiniteLine(angle=0, movable=True, hoverPen={'color': "FF0", 'width': 4})
        self.hline2 = pg.InfiniteLine(angle=0, movable=True, hoverPen={'color': "FF0", 'width': 4})
        self.vline1 = pg.InfiniteLine(angle=90, movable=True, hoverPen={'color': "FF0", 'width': 4})
        self.vline2 = pg.InfiniteLine(angle=90, movable=True, hoverPen={'color': "FF0", 'width': 4})

        self.hline1.setValue(0)
        self.vline1.setValue(0)
        self.vline2.setValue(max_size[0])
        self.hline2.setValue(max_size[1])
        self.hline1.setBounds((0, max_size[1]))
        self.hline2.setBounds((0, max_size[1]))
        self.vline1.setBounds((0, max_size[0]))
        self.vline2.setBounds((0, max_size[0]))
        self.view.addItem(self.hline1)
        self.view.addItem(self.hline2)
        self.view.addItem(self.vline1)
        self.view.addItem(self.vline2)
        self.corner_roi[0] = 0
        self.corner_roi[1] = 0

    def get_roi_values(self):
        """ Get's the ROI values in camera-space. It keeps track of the top left corner in order
        to update the values before returning.
        :return: Position of the corners of the ROI region assuming 0-indexed cameras.
        """
        y1 = round(self.hline1.value())
        y2 = round(self.hline2.value())

        x1 = round(self.vline1.value())
        x2 = round(self.vline2.value())

        X = np.sort((x1, x2))
        Y = np.sort((y1, y2))
        # Updates to the real values in camera space
        X += self.corner_roi[0]
        Y += self.corner_roi[1]
        X[1] -= 1
        Y[1] -= 1
        return X, Y

    def set_roi_lines(self, X, Y):
        self.corner_roi = [X[0], Y[0]]
        self.hline1.setValue(0)
        self.vline1.setValue(0)
        x2 = X[1]-X[0]+1
        y2 = Y[1]-Y[0]+1
        self.hline2.setValue(y2)  # To the last pixel
        self.vline2.setValue(x2)  # To the last pixel


    def setup_mouse_tracking(self):
        self.imv.setMouseTracking(True)
        self.imv.getImageItem().scene().sigMouseMoved.connect(self.mouseMoved)
        self.imv.getImageItem().scene().contextMenu = None

    def setup_mouse_click(self):
        self.img.scene().sigMouseClicked.connect(self.mouseClicked)
        self.connect_mouse_clicked(None)

    def connect_mouse_clicked(self, callback=None):
        """Link the mouse click to a function. Use None (default) to reset."""
        if callback is None:
            self.click_callback = lambda *args, **kwargs: None
        else:
            self.click_callback = callback

    def mouseClicked(self, arg):
        coord = self.img.mapFromScene(arg.pos())
        print(coord)
        self.click_callback([coord.x(), coord.y()])

    def keyPressEvent(self,key):
        """Triggered when there is a key press with some modifier.
        Shift+C: Removes the cross hair from the screen
        Ctrl+C: Emits a specialTask signal
        Ctrl+V: Emits a stopSpecialTask signal
        These last two events have to be handeled in the mainWindow that implemented this widget."""
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            if key.key() == 67: # For letter C of 'Clear
                if self.showCrosshair:
                    for c in self.crosshair:
                        self.view.removeItem(c)
                    self.showCrosshair = False
                if self.showCrossCut:
                    self.view.removeItem(self.crossCut)
                    self.showCrossCut = False
        elif modifiers == Qt.ControlModifier:
            if key.key() == 67: # For letter C of 'Clear
                self.specialTask.emit()
            if key.key() == 86: # For letter V
                self.stopSpecialTask.emit()

    def mouseMoved(self, arg):
        """Updates the position of the cross hair. The mouse has to be moved while pressing down the Ctrl button."""
        # arg = evt.pos()
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            if not self.showCrosshair:
                for c in self.crosshair:
                    self.view.addItem(c)
                self.showCrosshair = True
            self.crosshair[1].setValue(int(self.img.mapFromScene(arg).x()))
            self.crosshair[0].setValue(int(self.img.mapFromScene(arg).y()))
        elif modifiers == Qt.AltModifier:
            if not self.showCrossCut:
                self.view.addItem(self.crossCut)
            self.showCrossCut = True
            self.crossCut.setValue(int(self.img.mapFromScene(arg).y()))

    def do_auto_scale(self):
        h, y = self.img.getHistogram()
        self.imv.setLevels(min(h),max(h))

    def draw_target_pointer(self, locations):
        """gets an image and draws a circle around the target locations.

        :param DataFrame locations: DataFrame generated by trackpy's locate method. It only requires columns `x` and `y` with coordinates.
        """
        if locations is None:
            return

        # locations = locations[['y', 'x']].values
        brush = pg.mkBrush(color=(255, 0, 0))
        self.marker.setData(locations[0], locations[1], symbol='x', symbolBrush=brush)
        # COMMENT: change this from plotting a marker, to an actual box by drawing lines or a curve of the true shape
        #this is called all the time

    def update_image(self, image):
        self.img.setImage(image, autoLevels=False, autoRange=False, autoHistogramRange=False, axisOrder="row-major")
        if self.first_image:
            self.do_auto_scale()
            self.first_image = False

    def setup_cross_hair(self, max_size):
        """Sets up a cross hair."""
        self.crosshair = []
        self.crosshair.append(pg.InfiniteLine(angle=0, movable=False, pen={'color': 124, 'width': 4}))
        self.crosshair.append(pg.InfiniteLine(angle=90, movable=False, pen={'color': 124, 'width': 4}))
        self.crosshair[0].setBounds((1, max_size[1] - 1))
        self.crosshair[1].setBounds((1, max_size[0] - 1))
        #print("setup_cross_hair")

    def setup_cross_cut(self, max_size):
        """Set ups the horizontal line for the cross cut."""
        self.crossCut = pg.InfiniteLine(angle=0, movable=False, pen={'color': 'g', 'width': 2})
        self.crossCut.setBounds((1, max_size))
        #print("setup_cross_cut")


if __name__ == "__main__":
    from pandas import DataFrame

    app = QApplication([])
    win = CameraViewerWidget()
    data = np.random.randint(0, 125, (40, 100))
    win.update_image(data)

    # To test the click callback
    win.setup_mouse_click()
    win.connect_mouse_clicked(print)

    win.show()
    location = DataFrame([[20, 50], [30, 60]], columns=['x', 'y'])
    win.draw_target_pointer(location)
    app.exec()
