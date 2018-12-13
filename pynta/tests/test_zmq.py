"""
    Test the limits of the pyZMQ library
    =====================================

    Example on how to test the bandwidth limits for pyZMQ. We create a Queue with a given number of frames and an empty
    queue. The first is fed to the publisher, while the second is used by the subscriber to append the data. In this way
    we can check whether all the frames arrived in order and the bandwidth limitation for ZMQ.

    If any attempts at improve the architecture of publisher/subscriber are tried, this test is going to be useful to
    determine whether there is a real improvement in performance.

    .. note:: Replacing send_pyobj by the nocopy option is faster, however it also requires to reshape the data, which
    adds an overhead and eventually reaches equivalent bandwidths.

    .. warning:: This script consumes a lot of memory because it allocates a queue with thousands of elements in it. If
    you have a more limited system, consider lowering the amount of elements or changing the data type.

"""
from time import time

import numpy as np
from multiprocessing import Process, Queue

from pynta.model.experiment.publisher import publisher
from pynta.model.experiment.subscriber import subscriber
from pynta.util import get_logger


def test_func(data, queue):
    logger = get_logger(name=__name__)
    logger.info('Putting data to queue')
    queue.put(data)


def main(num_data_frames = 1000, dtype=np.uint16):
    data = np.random.randint(0, high=2**8, size=(1000, 1000), dtype=dtype)
    recv_q = Queue()  # Queue where data will be received
    send_q = Queue()
    for i in range(num_data_frames):
        send_q.put({'topic': 'test', 'data': data})
    send_q.put({'topic': 'test', 'data': 'stop'})
    send_q.put({'topic': '', 'stop_pub': 'stop_pub'})
    sub1 = Process(target=subscriber, args=[test_func, 'test', recv_q])
    sub1.start()
    t0 = time()
    pub = Process(target=publisher, args=[send_q])
    pub.start()
    pub.join()
    t1 = time() - 2 - t0  # The publishers sleeps for 2 seconds, 1 at the beginning, 1 at the end
    bandwidth = num_data_frames * data.nbytes / t1
    i = 0
    while not recv_q.empty() or recv_q.qsize() > 0:
        d = recv_q.get()
        i += 1
    return bandwidth, t1, i


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Test the limits of ZMQ on this system')
    parser.add_argument("--data-frame", dest="number_frames", default=1000,
                        help="Number of data frames to send")
    parser.add_argument("--data-type", dest="dtype",
                        default="uint8",
                        help="Data type to use, uint8, uint16, uint32")

    args = parser.parse_args()

    if args.dtype == 'uint8':
        dtype = np.uint8
    elif args.dtype == 'uint16':
        dtype = np.uint16
    elif args.dtype == 'uint32':
        dtype = np.uint32
    else:
        raise ValueError('Dtype must be either uint8, 16 or 32')

    num_frames = int(args.number_frames)
    print('Starting the test. It may take a couple of seconds to complete...')
    bandwidth, t, rcv_num_frames = main(num_data_frames=num_frames, dtype=dtype)
    print('Recevied {} frames out of {} sent'.format(num_frames, rcv_num_frames))
    print('Total execution time: {:3.1f}s'.format(t))
    print('Estimated bandwidth: {:3.1f}MB/s'.format(bandwidth/1024/1024))

    #
    # print('Total ellapsed time: {:2.1f}s'.format(t1-t0))
    #
    # print('Bandwidth: {:4.1f}MB/s'.format(bandwidth/1024/1024))
    #
    #
    # print('Total received points: {}/{}'.format(i, num_data_frames))
