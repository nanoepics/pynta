from multiprocessing import Process, Queue
from time import time

import numpy as np


def put_to_queue(queue):
    image = np.random.random((1200, 120))
    t00 = time()
    for i in range(5000):
        t0 = time()
        queue.put(image)
        print("P: {:3.4f}ms".format(1000 * (time() - t0)), end="\r")
    queue.put('Exit')
    print("\nAverage time to put: {:3.4}ms".format(1000 * (time() - t00) / i))


def get_from_queue(queue):
    i = 1
    t00 = time()
    for i in range(5000):
        t0 = time()
        img = queue.get()
        print("\t\tG: {:3.4f}ms".format(1000 * (time() - t0)), end="\r")
        i += 1
        # if type(img) == str:
        #     break
    print("\nAverage time to get: {:3.4}ms".format(1000 * (time() - t00) / i))


queue = Queue()
p1 = Process(target=put_to_queue, args=[queue])
p2 = Process(target=get_from_queue, args=[queue])
p1.start()
p2.start()
p1.join()
p2.join()