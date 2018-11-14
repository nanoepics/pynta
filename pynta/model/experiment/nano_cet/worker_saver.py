"""
    UUTrack.Model.workerSaver
    =========================
    When working with multi threading in Python it is important to define the function that will be run in a separate
    thread. workerSaver is just a function that will be moved to a separate, parallel thread to save data to disk
    without interrupting the acquisition.

    Since the workerSaver function will be passed to a different Process (via the *multiprocessing* package) the only
    way for it to receive data from other threads is via a Queue. The workerSaver will run continuously until it finds a
    string as the next item.

    To understand how the separate process is created, please refer to
    :meth:`~UUTrack.View.Camera.cameraMain.cameraMain.movieSave`

    The general principle is

        >>> filename = 'name.hdf5'
        >>> q = Queue()
        >>> metadata = _session.serialize() # This prints a YAML-ready version of the session.
        >>> p = Process(target=workerSaver, args=(filename, metaData, q,))
        >>> p.start()
        >>> q.put([1, 2, 3])
        >>> q.put('Stop')
        >>> p.join()

    :copyright: 2017

    .. sectionauthor:: Aquiles Carattino <aquiles@aquicarattino.com>
"""

import h5py
import numpy as np
from datetime import datetime


def worker_saver(file_path, meta, q):
    """Function that can be run in a separate thread for continuously save data to disk.

    .. TODO:: The memory allocation is fixed inline at 250MB and should be more flexible.

    :param str fileData: the path to the file to use.
    :param str meta: Metadata. It is kept as a string in order to provide flexibility for other programs.
    :param Queue q: Queue that will store all the images to be saved to disk.
    """

    with h5py.File(file_path, "a") as f:
        now = str(datetime.now())
        g = f.create_group(now)
        g.create_dataset('metadata', data=meta)

        keep_saving = True  # Flag that will stop the worker function if running in a separate thread.
        # Has to be submitted via the queue a string 'exit'

        i = 0
        j = 0
        first = True
        from pynta.util import get_logger
        logger = get_logger(__name__)
        while keep_saving:
            while not q.empty() or q.qsize() > 0:
                img = q.get()
                if isinstance(img, str):
                    keep_saving = False
                elif first:  # First time it runs, creates the dataset
                    x = img.shape[0]
                    y = img.shape[1]
                    allocate_memory = 250  # megabytes of memory to allocate on the hard drive.
                    allocate = int(allocate_memory / img.nbytes * 1024 * 1024)
                    logger.debug('Allocating 250MB to stream to disk')
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
                        dset[:, :, j:j + allocate] = d
                        dset.resize((x, y, j + 2 * allocate))
                        d = np.zeros((x, y, allocate), dtype=img.dtype)
                        i = 0
                        j += allocate
                    d[:, :, i] = img
                    i += 1

        if j > 0 or i > 0:
            logger.info('Saving last bits of data before stopping.')
            dset[:, :, j:j + allocate] = d  # Last save before closing

        logger.info('Flushing file to disk...')
        f.flush()
    logger.info('Finished writing to disk')


def clear_queue(q):
    """Clears the queue by reading it.

    :params q: Queue to be cleaned.
    """
    while not q.empty() or q.qsize() > 0:
        q.get()
