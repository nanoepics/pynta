# -*- coding: utf-8 -*-
"""
In this example we draw two different kinds of histogram.
"""

import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QGridLayout
import numpy as np

from pynta.model.experiment.nano_cet.decorators import make_async_thread


class TracksWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plot = pg.PlotWidget()
        self.layout = QGridLayout()
        self.layout.addWidget(self.plot)
        self.setLayout(self.layout)
        self._threads = []

    @make_async_thread
    def plot_trajectories(self, locations):
        """

        :param locations: Dataframe of locations as given by trackpy
        """
        unstacked = locations.set_index(['particle', 'frame'])[['x', 'y']].unstack()
        for i, trajectory in unstacked.iterrows():
            x = trajectory['x'].values
            y = trajectory['y'].values
            x = x[~np.isnan(x)]
            y = y[~np.isnan(y)]
            self.plot.plot(x, y)
