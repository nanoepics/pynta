"""
    UUTrack.View.Camera.clearQueueThread.py
    =======================================
    If one desires to clear the Queue without saving it, a thread should read all the elements of the Queue until it is empty. The documentation on Queues and Processes is a bit obscure as to know if there is a better way of deleting a Queue preserving its integrity.

    .. warning:: If this Thread is run while the save thread is running there will be data loss without warning. Moreover, of the clear queue destroys the last element of the Queue before the saver arrives to it, te saver will not stop.

    .. sectionauthor:: Aquiles Carattino <aquiles@aquicarattino.com>
"""

from pyqtgraph.Qt import QtCore
from time import sleep

class clearQueueThread(QtCore.QThread):
    """Clears the Queue.
    """
    def __init__(self,q):
        QtCore.QThread.__init__(self)
        self.q = q

    def __del__(self):
        self.wait()

    def run(self):
        """Clears the queue.
        """
        while self.q.qsize()>0:
            self.q.get()
