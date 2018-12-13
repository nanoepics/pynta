from copy import copy
from datetime import datetime

import h5py
import numpy as np
import trackpy as tp
from multiprocessing import Process, Event
from time import sleep
from pandas import DataFrame
from scipy.stats import stats
from trackpy.linking import Linker

from pynta import general_stop_event
from pynta.model.experiment.nano_cet.decorators import make_async_thread
from pynta.model.experiment.nano_cet.exceptions import DiameterNotDefined, LinkException
from pynta.model.experiment.subscriber import subscribe
from pynta.util import get_logger


class LocateParticles:
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
        self.logger.debug('Started tracking')
        self._tracking_event.clear()
        self._tracking_process = Process(
            target=calculate_locations,
            args=[self.publisher.port, topic, self._tracking_event, self.publisher._queue],
            kwargs=copy(self.config['locate']))
        self._tracking_process.start()

    def stop_tracking(self):
        self._tracking_event.set()

    def start_saving(self, file_path, meta):
        self._saving_event.clear()
        self._saving_process = Process(
            target=save_locations,
            args=[file_path, meta, self.publisher.port, self._saving_event])
        self._saving_process.start()

    def stop_saving(self):
        self._saving_event.set()

    def start_linking(self):
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
        self.calculating_histograms = True
        locations = self.locations.copy()
        t1 = tp.filter_stubs(locations, self.config['process']['min_traj_length'])
        # t2 = t1[((t1['mass'] > self.config['process']['min_mass']) & (t1['size'] < self.config['process']['max_size']) &
        #          (t1['ecc'] < self.config['process']['max_ecc']))]
        im = tp.imsd(t1, self.config['process']['um_pixel'], self.config['process']['fps'])
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
        locations = self.locations.copy()
        t1 = tp.filter_stubs(locations, self.config['process']['min_traj_length'])
        t2 = t1[((t1['mass'] > self.config['process']['min_mass']) & (t1['size'] < self.config['process']['max_size']) &
                 (t1['ecc'] < self.config['process']['max_ecc']))]
        return t2

    def stop_linking(self):
        self._linking_event.set()

    def finalize(self):
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
        locations = tp.locate(image, **kwargs)
        publisher_queue.put({'topic': 'locations', 'data': locations})


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
