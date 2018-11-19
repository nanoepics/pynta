from queue import Queue
from threading import Thread

import numpy as np
import zmq


class CameraWorker:
    """ This class is responsible for keeping the link with the camera and broadcasting the data through a ZMQ
    connection.
    """
    def __init__(self, camera):
        """ On creation, the CameraWorker will hold the communication with the camera.

        :param camera: An initialized model for a camera.
        """

        self.camera = camera
        port_pub = "5558"
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind("tcp://*:%s" % port_pub)

        port_sub = "5559"
        sub_context = zmq.Context()
        self.socket_sub = sub_context.socket(zmq.SUB)
        self.socket_sub.bind("tcp://*:%s" % port_sub)

        self.image_queue = Queue()
        self.command_queue = Queue()

        self.publish_thread = None
        self.subscriber_thread = None
        self.acquire_thread = None

        self.keep_acquiring = False

    def start(self):
        self.publish_thread = Thread(target=self.publish_image, args=[self.image_queue, self.socket])
        self.publish_thread.start()
        self.acquire_thread = Thread(target=self.acquire, args=[])
        self.acquire_thread.start()

    def acquire(self):
        self.keep_acquiring = True
        first = True
        while self.keep_acquiring:
            if first:
                self.camera.setAcquisitionMode(self.camera.MODE_CONTINUOUS)
                self.camera.triggerCamera()  # Triggers the camera only once
                first = False

            data = self.camera.readCamera()
            for img in data:
                self.image_queue.put(img)
        self.camera.stopAcq()

    @staticmethod
    def publish_image(queue, socket):
        while True:
            if not queue.empty():
                image = queue.get()
                if type(image) == str:
                    break

                md = dict(dtype=str(image.dtype),
                      shape=image.shape)
                socket.send_json(md, 0 | zmq.SNDMORE)
                socket.send(image, flags=0, copy=True, track=False)

    def stop(self):
        self.keep_acquiring = False
        self.image_queue.put('Exit')
        self.socket.close()
        self.socket_sub.close()

    def is_alive(self):
        return self.acquire_thread.is_alive() or self.publish_thread.is_alive()
