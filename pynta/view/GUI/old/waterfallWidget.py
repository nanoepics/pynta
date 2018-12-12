"""
    UUTrack.View.Camera.waterfallWidget.py
    ========================================
    Widget for displaying a 2D image. It shouldn't do much, but is thought for displaying a waterfall kind of image.

    .. todo:: displaying 2D data is ubiquitous in this program; there should be a unified widget to such ends.
    
    .. todo:: Unify the 2D displaying of :mod:`camera Main <UUTrack.View.Camera.cameraMain>` and :mod:`camera Viewer <UUTrack.View.Camera.cameraViewer>`.

    .. sectionauthor:: Aquiles Carattino <aquiles@aquicarattino.com>
"""

import pyqtgraph as pg
from pyqtgraph import GraphicsLayoutWidget
from pyqtgraph.Qt import QtGui


class waterfallWidget(QtGui.QWidget):
    """Widget for plotting a waterfall plot.
    """
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.layout = QtGui.QHBoxLayout(self)
        self.viewport = GraphicsLayoutWidget()
        self.view = self.viewport.addViewBox(colspan=3, rowspan=3, lockAspect = False, enableMenu=True)
        self.img = pg.ImageItem()
        self.view.addItem(self.img)

        self.h = self.viewport.addViewBox(enableMenu=False, colspan=3)
        self.hist = pg.HistogramLUTItem(image=self.img, fillHistogram=False)
        self.hist.setImageItem(self.img)
        self.h.addItem(self.hist)

        self.imv = pg.ImageView(view=self.view, imageItem=self.img)

        self.layout.addWidget(self.imv)
        self.setLayout(self.layout)

