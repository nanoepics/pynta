# -*- coding: utf-8 -*-
"""
    work_thread.py
    ===========
    Running the acquisition on a separate thread gives a lot of flexibility when designing the program. It comes,
    however with some potential risks. First, threads are still running on the same Python interpreter. Therefore they
    do not overcome the GIL limitations. They are able to share memory, which makes them transparent to less experienced
    users. Potentially, different threads will access the same resources (i.e. devices) creating a clash. It is hard to
    implement semaphores or locks for every possible scenario, especially with devices such as cameras which can run
    without user intervention for long periods of time.


    :copyright:  Aquiles Carattino <aquiles@aquicarattino.com>
    :license: AGPLv3, see LICENSE for more details
"""
from threading import Thread


class WorkerThread(Thread):
    """ Thread for acquiring from the camera. If the exposure time is long, running on a separate thread will enable
    to perform other tasks. It also allows to acquire continuously without freezing the rest of the program.

    .. TODO:: QThreads are much handier than Python threads. Should we put Qt as a requirement regardless of whether
    the program runs on CLI or UI mode?
    """
    def __init__(self, camera, keep_alive=False):
        super().__init__()
        self.camera = camera
        self.keep_alive = keep_alive

    def run(self):
        self.camera.triggerCamera()
