# -*- coding: utf-8 -*-
"""
In this example we draw two different kinds of histogram.
"""

import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QGridLayout
import numpy as np

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class HistogramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plot = pg.PlotWidget()
        self.plot.setLabel('left', '# Of Particles')
        self.plot.setLabel('bottom', 'Diffusion Coefficient', '<math>&mu; m<sup>2</sup>/s</math>')
        self.layout = QGridLayout()
        self.layout.addWidget(self.plot)
        self.setLayout(self.layout)

    def update_distribution(self, values):
        values = np.abs(values)
        y, x = np.histogram(values, bins=30)
        self.plot.plot(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 50), clear=True)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    win = HistogramWidget()
    win.show()
    vals = np.hstack([np.random.normal(size=500), np.random.normal(size=260, loc=4)])
    win.update_distribution(vals)
    sys.exit(app.exec())
