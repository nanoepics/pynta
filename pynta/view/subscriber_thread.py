# -*- coding: utf-8 -*-
"""
    Subscriber Thread
    =================
    Allows to transform topics coming from a socket (ZMQ) to Qt signals that can be connected to
    any method, etc.

    :copyright:  Aquiles Carattino <aquiles@aquicarattino.com>
    :license: GPLv3, see LICENSE for more details
"""
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

from pynta.model.experiment.subscriber import subscribe


class SubscriberThread(QThread):
    data_received = pyqtSignal(list)

    def __init__(self, port, topic):
        super().__init__()
        self.topic = topic
        self.port = port
        self.keep_receiving = True

    def __del__(self):
        self.keep_receiving = False
        self.wait()

    def run(self):
        socket = subscribe(self.port, self.topic)
        while self.keep_receiving:
            socket.recv_string()
            data = socket.recv_pyobj()  # flags=0, copy=True, track=False)
            self.data_received.emit(data)
