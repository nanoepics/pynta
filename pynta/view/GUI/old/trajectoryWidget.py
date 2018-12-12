"""
    UUTrack.View.Camera.trajectoryWidget.py
    ========================================
    This widget only displays the output of the special worker. It is mainly for prototyping purposes. It displays a scatter 2D plot because it is the current output of the special task worker, but in principle it can be adapted to any other need.

    .. todo:: adapt this widget for a useful case.

    .. sectionauthor:: Aquiles Carattino <aquiles@aquicarattino.com>
"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui


class trajectoryWidget(pg.GraphicsView):
    """Simple plot class for showing the 2D trajectory"""
    def __init__(self,parent=None):
        # QtGui.QWidget.__init__(self, parent)
        super(trajectoryWidget, self).__init__()
        #self.layout = QtGui.QHBoxLayout(self)

        #gv = pg.GraphicsView()
        self.l = QtGui.QGraphicsGridLayout()
        self.l.setHorizontalSpacing(0)
        self.l.setVerticalSpacing(0)

        self.vb = pg.ViewBox()

        self.plot = pg.PlotDataItem()
        self.vb.addItem(self.plot)
        self.l.addItem(self.vb, 0, 1)
        self.centralWidget.setLayout(self.l)
        self.xScale = pg.AxisItem(orientation='bottom', linkView=self.vb)
        self.l.addItem(self.xScale, 1, 1)
        self.yScale = pg.AxisItem(orientation='left', linkView=self.vb)
        self.l.addItem(self.yScale, 0, 0)

        self.xScale.setLabel('X Axis', units='px')
        self.yScale.setLabel('Y Axis', units='px')
        #self.view = pg.GraphicsLayoutWidget()
        #
        # self.vb = pg.ViewBox()
        # self.plot = pg.PlotItem()
        # self.vb.addItem(self.plot)
        # self.layout.addWidget(self.vb)
        # self.setLayout(self.layout)

if __name__ == '__main__':
    from PyQt4.Qt import QApplication
    import sys
    import numpy as np

    app = QApplication(sys.argv)
    t = trajectoryWidget()
    def rand(n):
        data = np.random.random(n)
        data[int(n*0.1):int(n*0.13)] += .5
        data[int(n*0.18)] += 2
        data[int(n*0.1):int(n*0.13)] *= 5
        data[int(n*0.18)] *= 20
        return data, np.arange(n, n+len(data)) / float(n)

    yd, xd = rand(10000)
    t.plot.setData(y=yd, x=xd)

    t.show()
    sys.exit(app.exec_())
