import h5py
import numpy as np
from datetime import datetime
from pynta.util.log import get_logger


def add_to_save_queue(data, queue_saver):
    """ This method is a buffer between the publisher and the ``save_stream`` method. The idea is that in order
    to be quick (saving to disk may be slow), whatever the publisher sends will be added to a Queue. Another
    process will read from the queue and save it to disk on a separate process.
    """
    img = data[1]
    queue_saver.put(img)


def worker_saver(file_path, meta, q, max_memory=500):
    """Function that can be run in a separate thread for continuously save data to disk.

    :param str file_path: the path to the file to use.
    :param str meta: Metadata. It is kept as a string in order to provide flexibility for other programs.
    :param Queue q: Queue that will store all the images to be saved to disk.
    :param int max_memory: Maximum memory (in MB) to allocate
    """
    logger = get_logger(name=__name__)
    logger.info('Appending data to {}'.format(file_path))
    allocate_memory = max_memory  # megabytes of memory to allocate on the hard drive.

    with h5py.File(file_path, "a") as f:
        now = str(datetime.now())
        g = f.create_group(now)
        g.create_dataset('metadata', data=meta.encode("ascii","ignore"))
        keep_saving = True  # Flag that will stop the worker function if running in a separate thread.
        # Has to be submitted via the queue a string 'exit'

        i = 0
        j = 0
        first = True

        while keep_saving:
            while not q.empty() or q.qsize() > 0:
                img = q.get()
                if isinstance(img, str):
                    keep_saving = False
                    logger.info('Got the signal to stop the saving')
                    continue

                if first:  # First time it runs, creates the dataset
                    x = img.shape[0]
                    y = img.shape[1]
                    logger.debug('Image size: {}x{}'.format(x, y))
                    allocate = int(allocate_memory / img.nbytes * 1024 * 1024)
                    logger.debug('Allocating {}MB to stream to disk'.format(allocate_memory))
                    logger.debug('Allocate {} frames'.format(allocate))
                    d = np.zeros((x, y, allocate), dtype=img.dtype)
                    dset = g.create_dataset('timelapse', (x, y, allocate), maxshape=(x, y, None),
                                            compression='gzip', compression_opts=1,
                                            dtype=img.dtype)  # The images are going to be stacked along the z-axis.
                    d[:, :, i] = img
                    i += 1
                    first = False
                else:
                    if i == allocate:
                        logger.debug('Allocating more memory')
                        dset[:, :, j:j + allocate] = d
                        dset.resize((x, y, j + 2 * allocate))
                        d = np.zeros((x, y, allocate), dtype=img.dtype)
                        i = 0
                        j += allocate
                    d[:, :, i] = img
                    i += 1

        if j > 0 or i > 0:
            logger.info('Saving last bits of data before stopping.')
            logger.debug('Missing values: {}'.format(i))
            dset[:, :, j:j + i] = d[:, :, :i]  # Last save before closing

        # This last bit is to avoid having a lot of zeros at the end of the timelapses
        dset.resize((x, y, j+i))

        logger.info('Flushing file to disk...')
        f.flush()
    logger.info('Finished writing to disk')


def clear_queue(q):
    """Clears the queue by reading it.

    :params q: Queue to be cleaned.
    """
    while not q.empty() or q.qsize() > 0:
        q.get()
