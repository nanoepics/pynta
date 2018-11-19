from multiprocessing import Queue, Process
from time import sleep

import numpy as np
import zmq


class Publisher:
    """ General Publisher class that creates a socket for publishing whatever is in the queue.
    """
    def __init__(self):
        self.port_pub = 5555
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        # self.socket.bind("tcp://*:%s" % self.port_pub)
        self.socket_bind()
        sleep(1)
        self.queue = None
        self._process = None
        image = np.random.random((1200, 120))
        self.socket.send_pyobj(image)
        image = np.random.random((1200, 120))
        self.socket.send_pyobj(image)

    def socket_bind(self):
        try:
            self.socket.bind("tcp://*:%s" % self.port_pub)
        except zmq.error.ZMQError:
            self.port_pub += 1
            self.socket_bind()

    def start(self):
        self.queue = Queue()
        self._process = Process(target=publish, args=[self.queue, self.socket])
        self._process.start()

    def stop(self):
        self.queue.put('stop')
        self._process.join()

    def __str__(self):
        return "Publisher on port {}".format(self.port_pub)


def publish(queue):
    """ Static method for publishing elements from a queue through a socket.

    :param queue: Queue from where the elements are acquired
    :param socket: Socket used for broadcasting the data
    """
    port_pub = 5555
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:%s" % port_pub)
    sleep(1)
    print(socket)
    while True:
        if not queue.empty():
            message = queue.get()
            print(message)
            # socket.send_string('', zmq.SNDMORE)
            # socket.send_pyobj(message)
            # image = np.random.random((1200, 120))
            socket.send_pyobj(message)
            if type(message) == str:
                if message == 'stop':
                    break
    print('Stopping publish')


if __name__ == "__main__":

    queue = Queue()
    p = Process(target=publish, args=[queue])
    queue.put(np.random.random((100, 100)))
    queue.put(np.random.random((100, 100)))
    queue.put('stop')
    p.start()
    p.join(timeout=5)
    # p = Publisher()
    # p.start()
    # print(p)
    # while True:
    #     try:
    #         p.queue.put([1, 2, 3, 4])
    #         sleep(1)
    #     except KeyboardInterrupt:
    #         break
    # print('Queue length: {}'.format(p.queue.qsize()))
    # p.stop()