# -*- coding: utf-8 -*-
"""
Localization Routines
=====================
Tracking particles is a relatively easy routine. PyNTA uses trackpy to analyse every frame that is generated. However,
linking localizations in order to build a trace is not trivial, since it implies preserving in memory the previous
locations. The main idea of these routines is that a main object :class:`~LocateParticles` holds the information of
the processes running. Moreover, there is a combination of threads and processes depending on the expected load.

It has to be noted that Windows has a peculiar way of dealing with new processes that prevents us from using methods,
but instead we are forced to use functions. This is very limiting but couldn't find a way around yet.

The core idea is that the localization uses the data broadcasted by :class:`~nanoparticle_tracking.model.experiment.publisher.Publisher`
in order to collect new frames, or save localizations to disk. It uses the
:class:`~nanoparticle_tracking.model.experiment.subscriber.Subscriber` in order to listen for the new data, and in turn publishes it
with the Publisher.

:copyright:  Aquiles Carattino <aquiles@uetke.com>
:license: GPLv3, see LICENSE for more details
"""
from copy import copy
from datetime import datetime

import h5py
import numpy as np
import trackpy as tp
from multiprocessing import Process, Event
from time import sleep, time
from pandas import DataFrame
from scipy.stats import stats
from trackpy.linking import Linker

from pynta import general_stop_event
from pynta.model.experiment.nanoparticle_tracking.decorators import make_async_thread
from pynta.model.experiment.nanoparticle_tracking.exceptions import DiameterNotDefined, LinkException
from pynta.model.experiment.subscriber import subscribe
from pynta.util import get_logger


class LocateParticles:
    """ Convenience class to keep track of processes and threads related to the localization of particles.
    The idea was to make it more robust when stopping processes and to give a common interface to the experiment in
     case radical changes are implemented. For example, changing tracking or linking algorithms, etc.
     """
    def __init__(self, publisher, config):
        self._accumulate_links_event = Event()
        self.publisher = publisher
        self._tracking_process = None
        self._tracking_event = Event()
        self._linking_process = None
        self._linking_event = Event()
        self._saving_process = None
        self._saving_event = Event()
        self.config = config

        self.locations = DataFrame()
        self.particle_ids = None

        self.calculating_histograms = False
        self.histogram_values = []

        self._threads = []

        self.logger = get_logger(name=__name__)
        self.logger.info('Initialized locate particles')

    def start_tracking(self, topic):
        """ Starts a process that listens for frames on a specific topic. It uses the function
        :func:`~calculate_locations`. The process is stored in ``self._trackings_process`` and is automatically started.

        :param str topic: Topic in which to listen for new frames.

        .. TODO:: Implement a lock to prevent more than one process to start
        """

        self.logger.debug('Started tracking')
        self._tracking_event.clear()
        self._tracking_process = Process(
            target=calculate_locations,
            args=[self.publisher.port, topic, self._tracking_event, self.publisher._queue],
            kwargs=copy(self.config['locate']))
        self._tracking_process.start()

    def stop_tracking(self):
        """ Stops the tracking process by setting a particular event.

        .. TODO:: This is a hard stop, i.e., tracking will stop immediately. Perhaps it would be wise to clear the queue.
        """
        self._tracking_event.set()

    def start_saving(self, file_path, meta):
        """ Starts a process for saving localizations to an HDF5 file. It uses the function :func:`~save_locations`.

        :param str file_path: Full path to the location where to save the data
        :param dict meta: Metadata as a dictionary. It will be serialized with json

        .. TODO:: Implement a lock to prevent a second process starting
        """
        self._saving_event.clear()
        self._saving_process = Process(
            target=save_locations,
            args=[file_path, meta, self.publisher.port, self._saving_event])
        self._saving_process.start()

    def stop_saving(self):
        """ Stops the saving process.

        .. TODO:: Implement a way of stop the saving after saving everything and not immediately.
        """
        self._saving_event.set()

    def start_linking(self):
        """ Starts a process to link the localizations of particles. It publishes the track information as a table,
        with the frame and particle number appended to the rightmost columns respectively. This particular task may be
        very time consuming.

        .. warning:: Linking tracks can block a process if there are too many particles with a very large search radius.
            If linking is too slow consider saving the localizations and link them afterwards.
        """
        self.logger.debug('Started the linking process')
        self._linking_event.clear()
        self._linking_process = Process(
            target=link_locations,
            args=[self.publisher.port, 'locations', self._linking_event, self.publisher._queue],
            kwargs=copy(self.config['link'])
        )
        self._linking_process.start()
        self.accumulate_links()

    @make_async_thread
    def accumulate_links(self):
        """ Asynchronous method to store the links in this class. It looked like a good idea to keep this information in
        a single location, regardless of whether another process is listening on the topic. This in principle can be
        used to analyse data retrospectively.

        .. todo:: Still needs to clear the memory after several calls. Need to fit better in the architecture of the
            program
        """
        self._accumulate_links_event.clear()
        socket = subscribe(self.publisher.port, 'particle_links')
        while not self._accumulate_links_event.is_set():
            if general_stop_event.is_set():
                break

            topic = socket.recv_string()
            data = socket.recv_pyobj()
            if self.locations.shape[0] == 0:
                self.locations = data[0]
            else:
                self.locations = self.locations.append(data[0])

    def stop_accumulate_links(self):
        self._accumulate_links_event.set()

    @make_async_thread
    def calculate_histogram(self):
        """ Starts a new thread to calculate the histogram of fit-parameters based on the mean-squared displacement of
        individual particles. It publishes the data on topic `histogram`.

        .. warning:: This method is incredibly expensive. Since it runs on a thread it can block other pieces of code,
        especially the GUI, which runs on the same process.

        .. TODO:: The histogram loops over all the particles. It would be better to skeep particles for which there is
            no new data

        .. TODO:: Make this method able to run on a separate process. So far is not possible because it relies on data
            stored on the class itself (`self.locations`).
        """
        self.calculating_histograms = True
        locations = self.locations.copy()
        t1 = tp.filter_stubs(locations, self.config['process']['min_traj_length'])
        t2 = t1[((t1['mass'] > self.config['process']['min_mass']) & (t1['size'] < self.config['process']['max_size']) &
                 (t1['ecc'] < self.config['process']['max_ecc']))]
        im = tp.imsd(t2, self.config['process']['um_pixel'], self.config['process']['fps'])
        self.histogram_values = []
        for pcle in im:
            if general_stop_event.is_set():
                break

            data = im[pcle]
            t = data.index[~np.isnan(data.values)]
            val = data.values[~np.isnan(data.values)]
            try:
                slope, intercept, r, p, stderr = stats.linregress(np.log(t), np.log(val))
                self.histogram_values.append([slope, intercept])
            except:
                pass
        self.calculating_histograms = False
        self.publisher.publish('histogram', self.histogram_values)

    def relevant_tracks(self):
        """ Returns the relevant tracks as filtered by length, eccentricity, size and mass. This step needs careful
        consideration and should definitely be used in post-processing or once the parameters have been validated.
        """
        locations = self.locations.copy()
        t1 = tp.filter_stubs(locations, self.config['process']['min_traj_length'])
        t2 = t1[((t1['mass'] > self.config['process']['min_mass']) & (t1['size'] < self.config['process']['max_size']) &
                 (t1['ecc'] < self.config['process']['max_ecc']))]
        return t2

    def stop_linking(self):
        self._linking_event.set()

    def finalize(self):
        """ Stops all the processes and threads. It should be invoked when finishing a measurement or when stopping an
        acquisition.
        """
        self.stop_saving()
        self.stop_tracking()
        self.stop_linking()
        self.stop_accumulate_links()
        for thread in self._threads:
            if thread[1].is_alive():
                self.logger.warning('Finalizing a running thread: {}'.format(thread[0]))

    def __del__(self):
        self.stop_tracking()
        self.stop_saving()


def calculate_locations(port, topic, event, publisher_queue, **kwargs):
    socket = subscribe(port, topic)
    if 'diameter' not in kwargs:
        raise DiameterNotDefined('A diameter is mandatory for locating particles')

    while not event.is_set():
        socket.recv_string()
        data = socket.recv_pyobj()  # flags=0, copy=True, track=False)
        image = data[1]  # image[0] is the timestamp of the frame
        # t0 = time()
        locations = tp.locate(image, **kwargs)
        # loc_time = time()-t0
        publisher_queue.put({'topic': 'locations', 'data': locations})
        # publisher_queue.put({'topic': 'locations_time', 'data': [loc_time, len(locations)]})


def save_locations(file_path, meta, port, event, topic='locations'):
    socket = subscribe(port, topic)
    with h5py.File(file_path, 'a') as f:
        now = str(datetime.now())
        g = f.create_group(now)
        g.create_dataset('metadata', data=meta.encode('ascii', 'ignore'))
        f.flush()
        i = 0
        last_x = 0
        while not event.is_set():
            topic = socket.recv_string()
            data = socket.recv_pyobj()
            data = data.values
            data = data
            x, y = data.shape[0], data.shape[1]  # The first values is the number of rows, h5py uses the opposite notation
            if i == 0:
                dset = g.create_dataset('locations', (x, y+1), maxshape=(None, y+1))
            else:
                dset.resize((x+last_x, y+1))
            dset[last_x:last_x+x, 0] = i
            dset[last_x:last_x+x, 1:] = data
            last_x += x
            i += 1
            f.flush()


def calculate_locations_image(image, publisher_queue, locations_queue, **kwargs):
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

    logger.debug('Calculating positions with trackpy')
    locations = tp.locate(image, diameter, **kwargs)
    logger.debug('Got {} locations'.format(len(locations)))
    publisher_queue.put({'topic': 'trackpy_locations', 'data': locations})
    locations_queue.put(locations)


def link_locations(port, topic, event, publisher_queue, **kwargs):

    if 'search_range' not in kwargs:
        raise LinkException('Search Range must be specified')

    socket = subscribe(port, topic)
    t = 0  # First frame
    linker = Linker(**kwargs)
    while not event.is_set():
        topic = socket.recv_string()
        locations = socket.recv_pyobj()
        coords = np.vstack((locations['x'], locations['y'])).T
        if t == 0:
            linker.init_level(coords, t)
        else:
            linker.next_level(coords, t)
        t += 1
        locations['particle'] = linker.particle_ids
        locations['frame'] = t
        publisher_queue.put({'topic': 'particle_links', 'data': [locations, linker.particle_ids]})


def add_linking_queue(data, queue):
    logger = get_logger(__name__)
    logger.debug('Adding data frame to linking queue')
    queue.put(data)


def link_queue(locations_queue, publisher_queue, links_queue, **kwargs):
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
        if not locations_queue.empty() or locations_queue.qsize() > 0:
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
            links_queue.put(locations)
    logger.info('Stopping link queue trajectories')


def add_links_to_queue(data, queue):
    queue.put(data)


def calculate_histogram_sizes(tracks_queue, config, out_queue):
    params = config['tracking']['process']
    df = DataFrame()
    sleep(5)
    while True:
        while not tracks_queue.empty() or tracks_queue.qsize() > 0:
            data = tracks_queue.get()
            df = df.append(data)

        if len(df) % 100 == 0:
            # t1 = tp.filter_stubs(df, params['min_traj_length'])
            # print(t1.head())
            # t2 = t1[((t1['mass'] > params['min_mass']) & (t1['size'] < params['max_size']) &
            #          (t1['ecc'] < params['max_ecc']))]
            # print(t2.head())
            # t2 = t1
            # d = tp.compute_drift(t1)
            # tm = tp.subtract_drift(t2.copy(), d)
            im = tp.imsd(df, config['tracking']['process']['um_pixel'], config['camera']['fps'])
            values = []
            for pcle in im:
                data = im[pcle]
                slope, intercept, r, p, stderr = stats.linregress(np.log(data.index), np.log(data.values))
                values.append([slope, intercept])

            out_queue.put(values)

        # if len(df) > 100:
        #     break
