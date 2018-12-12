"""
    UUTrack.View.Camera.crossCut.py
    ===================================
    Window that displays a 1D plot of a cross cut on the main window.

    .. sectionauthor:: Aquiles Carattino <aquiles@aquicarattino.com>
"""

import pyqtgraph as pg
import numpy as np
import copy
from pyqtgraph.Qt import QtGui


class crossCutWindow(QtGui.QMainWindow):
    """
    Simple window that relies on its parent for updating a 1-D plot.
    """
    def __init__(self, parent=None):
        super(crossCutWindow, self).__init__(parent=parent)
        self.cc = pg.PlotWidget()
        self.setCentralWidget(self.cc)
        self.parent = parent
        y = np.random.random(100)
        self.p = self.cc.plot()
        changingLabel = QtGui.QLabel()
        font = changingLabel.font()
        font.setPointSize(16)
        self.text =  pg.TextItem(text='', color=(200, 200, 200), border='w', fill=(0, 0, 255, 100))
        self.text.setFont(font)
        self.cc.addItem(self.text)
        self.cc.setRange(xRange=(0,100), yRange=(-20,500))

    def update(self):
        """ Updates the 1-D plot. It is called externally from the main window.
        """
        if self.parent != None:
            if len(self.parent.tempimage) > 0:
                s = self.parent.camWidget.crossCut.value()
                (w,h) = np.shape(self.parent.tempimage)
                self.cc.setXRange(0,w)
                if s<h:
                    d = copy.copy(self.parent.tempimage[:, s])
                    if (self.parent.subtract_background and len(self.parent.bgimage) >= 1):
                        bg = self.parent.bgimage[:, s]
                        d = d - bg
                    self.p.setData(d)
                    if np.mean(d) > 0:
                        self.text.setText('Line %d\t Average: %d\t Max: %d\t' %(s, np.mean(d), np.max(d)))
            else:
                self.text.setText("Blank image")



if __name__ == '__main__':
    import numpy as np
    app = QtGui.QApplication([])
    win = crossCutWindow()
    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    win.cc.plot(x,y)
    win.show()
    app.instance().exec_()
