from multiprocessing import Queue

import numpy as np
from trackpy.linking import Linker

from pynta.model.experiment.nano_cet.exceptions import DiameterNotDefined
from pynta.util import get_logger

try:
    import trackpy as tp
    trackpy = True
except:
    trackpy = False


def calculate_positions_image(image, queue, **kwargs):
    """ Calculates the positions of the particles on an image. It used the trackpy package, which may not be
    installed by default.
    """
    if not 'diameter' in kwargs:
        raise DiameterNotDefined('A diameter is mandatory for locating particles')

    diameter = kwargs['diameter']
    del kwargs['diameter']
    image = image[1]  # image[0] is the timestamp of the frame
    logger = get_logger(name=__name__)
    logger.debug('Calculating positions on image')
    if trackpy:
        logger.debug('Calculating positions with trackpy')
        locations = tp.locate(image, diameter, **kwargs)
        logger.debug('Got {} locations'.format(len(locations)))
        queue.put({'topic': 'trackpy_locations', 'data': locations})


def add_linking_queue(data, queue):
    logger = get_logger(__name__)
    logger.debug('Adding data frame to linking queue')
    queue.put(data)


def link_queue(locations_queue, publisher_queue, **kwargs):
    """ Links the locations of particles from a location queue.
    It is a reimplementation of the link_iter of trackpy.
    """
    logger = get_logger(name=__name__)
    logger.info('Starting to create trajectory links from queue')
    t = 0  # First frame
    search_range = kwargs['search_range']
    del kwargs['search_range']
    linker = Linker(search_range, **kwargs)
    while True:
        if not locations_queue.empty():
            locations = locations_queue.get()
            if isinstance(locations, str):
                logger.debug('Got string on coordinates')
                break

            coords = np.vstack((locations['x'], locations['y'])).T
            if t == 0:
                logger.debug('First set of coordinates')
                linker.init_level(coords, t)
            else:
                logger.debug('Processing frame {}'.format(t))
                linker.next_level(coords, t)
            logger.debug("Frame {0}: {1} trajectories present.".format(t, len(linker.particle_ids)))
            t += 1
            locations['particle'] = linker.particle_ids
            locations['frame'] = t
            publisher_queue.put({'topic': 'particle_links', 'data': [locations, linker.particle_ids]})

    logger.info('Stopping link queue trajectories')


def add_links_to_queue(data, queue):
    queue.put(data)
