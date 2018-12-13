import logging
from time import sleep, time

import numpy as np
from multiprocessing import Process, Queue

from pynta.model.experiment.publisher import publisher
from pynta.model.experiment.subscriber import subscriber
from pynta.util import get_logger

logger = get_logger(name='pynta.model.experiment.subscriber')  # 'pynta.model.experiment.nano_cet.saver'
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

num_data_frames = 1000

data = np.random.randint(0, high=2**8, size=(1000, 1000), dtype=np.uint8)
recv_q = Queue()  # Queue where data will be received
send_q = Queue()
for i in range(num_data_frames):
    send_q.put({'topic': 'test', 'data': data})
send_q.put({'topic': 'test', 'data': 'stop'})
send_q.put({'topic': '', 'stop_pub': 'stop_pub'})


def test_func(data, queue):
    logger = get_logger(name=__name__)
    logger.info('Putting data to queue')
    queue.put(data)


def empty_func(data):
    pass


if __name__ == '__main__':
    sub1 = Process(target=subscriber, args=[test_func, 'test', recv_q])
    sub1.start()
    t0 = time()
    publisher = Process(target=publisher, args=[send_q])
    publisher.start()
    publisher.join()
    t1 = time()-2  # The publishers sleeps for 2 seconds, 1 at the beginning, 1 at the end
    print('Total ellapsed time: {:2.1f}s'.format(t1-t0))
    bandwidth = num_data_frames*data.nbytes/(t1-t0)
    print('Bandwidth: {:4.1f}MB/s'.format(bandwidth/1024/1024))
    i = 0
    while not recv_q.empty() or recv_q.qsize() > 0:
        d = recv_q.get()
        i += 1

    print('Total received points: {}/{}'.format(i, num_data_frames))
