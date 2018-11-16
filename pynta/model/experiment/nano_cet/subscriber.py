"""
    subscriber.py
    =============
    Example script on how to run separate processes to process the data coming from a publisher like the one on
    ``publisher.py``. The first process just grabs the frame and puts it in a Queue. The Queue is then used by
    another process in order to analyse, process, save, etc. It has to be noted that on UNIX systems, getting
    from a queue with ``Queue.get()`` is particularly slow, much slower than serializing a numpy array with
    cPickle.
"""
from multiprocessing import Queue, Process

import zmq
import numpy as np
from time import time


def subscriber():
    """ General subscriber which only listens on a specific port.
    Designed to check performance.
    """
    port = "5556"

    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    print("Collecting images from server...")
    socket.connect("tcp://localhost:%s" % port)

    topicfilter = b""
    socket.setsockopt(zmq.SUBSCRIBE, topicfilter)

    i = 1
    total_time = 0
    while True:
        t0 = time()
        md = socket.recv_json(flags=0)
        msg = socket.recv(flags=0, copy=True, track=False)
        if 'stop' in md:
            break
        img = np.frombuffer(msg, dtype=md['dtype'])
        this_time = time() - t0
        total_time += this_time
        print("P: {:3.4f}ms".format(1000 * this_time, end="\r"))
        i += 1
        if type(img) == str:
            break
    print('\nAverage time to read: {:3.4f}ms'.format(1000 * total_time / i))
    print('Received {} images in total'.format(i))


def put_to_queue(queue):
    port = "5556"

    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    print("Collecting images from server...")
    socket.connect("tcp://localhost:%s" % port)

    topicfilter = b""
    socket.setsockopt(zmq.SUBSCRIBE, topicfilter)

    # Process 5 updates
    total_value = 0
    i = 1
    t00 = time()
    while True:
        t0 = time()
        img = socket.recv_pyobj()
        queue.put(img)
        print("P: {:3.4f}ms".format(1000 * (time() - t0) ), end="\r")
        i += 1
        if type(img) == str:
            queue.put('exit')
            break
    print('\nAverage time to put into queue: {:3.4f}ms'.format(1000*(time()-t00)/i))

def consume_queue(queue):
    i = 1
    t00 = time()
    while True:
        t0 = time()
        img = queue.get()
        print("\t\t\t\t\tC: {:3.4f}ms".format(1000*(time()-t0)), end="\r")
        i += 1
        if type(img) == str:
            break

    print('\nAverage time to consume from queue: {:3.4f}ms'.format(1000*(time() - t00) / i))

def consume_queue2(queue):
    i = 0
    while True:
        img = queue.get()
        print("\t\t\t Queue size: ",queue.qsize(), end='\n')
        if type(img) == str:
            break

p_subscriber = Process(target=subscriber, args=[])
p_subscriber.start()
p_subscriber.join()

# queue = Queue()
# p1 = Process(target=consume_queue, args=[queue])
# p1.start()
# p2 = Process(target=put_to_queue, args=[queue])
# p2.start()
# queue2 = Queue()
# p3 = Process(target=consume_queue2, args=[queue])
# p4 = Process(target=put_to_queue, args=[queue])
# p3.start()
# p4.start()
# p1.join()
# p2.join()
# p3.join()
# p4.join()