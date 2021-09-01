# -*- coding: utf-8 -*-
"""
In this example we draw two different kinds of histogram.
"""

import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QGridLayout
import numpy as np
from collections import deque

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class GraphMonitorWidget(QWidget):
    def __init__(self, ylabel='', yunits=None, xlabel='time', xunits='s',parent=None):
        super().__init__(parent)
        self.plot = pg.PlotWidget()
        self.plot.setLabel('left', ylabel, units=yunits)
        self.plot.setLabel('bottom', xlabel, units=xunits)
        self.layout = QGridLayout()
        self.layout.addWidget(self.plot)
        self.setLayout(self.layout)

        self.set_window_duration(3)
        self.define_pens(2, 12)
        self.release_pen(-1)  # initializes
        self._data = {}

        # For testing purposes:
        self.k = 1
        self.c = 50
        self.test_timer = pg.QtCore.QTimer()
        self.test_timer.timeout.connect(self.fake_plot)
        # self.test_timer.start(100)

    # For testing purposes:
    def fake_plot(self):
        self.c -= 1
        if self.c<=0:
            self.test_timer.stop()
        if self.c ==40:
            self.plot.addLegend()
        dat = {}
        for m in range(self.k):
            if m>2 or self.c//4%2:
                dat[m] = m + 0.1*np.random.random()
        self.k = min(self.k + 1, self._max_colors*2)
        self.update_graph(dat)



    def set_window_duration(self, seconds, gui_update_time_s=0.1):
        self.window_duration_s = seconds
        self._buffer_duration_s = seconds + gui_update_time_s

    def define_pens(self, width=2, max_colors=10):
        self._line_width = width
        self._max_colors = max_colors
        self._brightness_percentage = 90
        self._pens = [pg.mkPen(pg.intColor(i, self._max_colors+1).lighter(self._brightness_percentage), width=self._line_width) for i in range(self._max_colors)]

    def pick_pen(self):
        """Picks a pen that is furthest "away" from the colors already in use"""
        self.landscape = np.zeros(self._max_colors)
        un, cnt = np.unique(self._pen_indices_in_use,  return_counts=True)
        cnt = cnt.astype(float)
        if self._pen_indices_in_use:
            cnt[int(np.where(un == self._pen_indices_in_use[-1])[0])] += 0.9/self._max_colors
            if len(self._pen_indices_in_use) > 1:
                cnt[int(np.where(un == self._pen_indices_in_use[-2])[0])] += 0.45/ self._max_colors
        for i in range(self._max_colors):
            dist = np.abs((un - i - self._max_colors/2) % self._max_colors - self._max_colors/2)
            self.landscape[i] = np.sum(cnt/(1+dist**0.5))
        if len(un):
            self.landscape[un] += cnt * self._max_colors
        pen_index = np.argmin(self.landscape)
        self._pen_indices_in_use.append(pen_index)
        return pen_index

    def release_pen(self, pen_index):
        """pass integer index of pen to release, -1 to release all"""
        if pen_index == -1:
            self._pen_indices_in_use = []
            self._pen_distance = np.zeros(self._max_colors)
            self.__last_released = None
        elif pen_index in self._pen_indices_in_use:
            self._pen_indices_in_use.remove(pen_index)
            self.__last_released = pen_index

    def update_graph(self, data_points):
        """This version takes care of time axis, you only pass values"""
        if self._data == {}:
            self.release_pen(-1)
            self.__start_time = pg.time()
        stamp = pg.time() - self.__start_time
        self.plot.setXRange(stamp - self.window_duration_s, stamp)
        for label, value in data_points.items():
            if label not in self._data:
                pen_index = self.pick_pen()
                curve = self.plot.plot([],[], pen=self._pens[pen_index], name=label)
                self._data[label] = {'curve': curve, 'pen_index': pen_index, 'time': deque(), 'values': deque()}
            self._data[label]['time'].append(stamp)
            self._data[label]['values'].append(value)
        empty = []
        for label, dat in self._data.items():
            while dat['time'] and dat['time'][0] < stamp - self._buffer_duration_s:
                dat['time'].popleft()
                dat['values'].popleft()
            if not dat['time']:
                empty.append(label)
            dat['curve'].setData(dat['time'], dat['values'])
        for label in empty:
            self.release_pen(self._data[label]['pen_index'])
            del self._data[label]


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])

    win = GraphMonitorWidget(ylabel='pixel brightness', yunits='counts')
    win.test_timer.start(100)
    win.show()

    app.exec()

