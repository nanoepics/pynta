# -*- coding: utf-8 -*-
"""
    Nanospring Tracking
    =====================

    Nanoparticle tracking analysis (NTA) is a common name used to the entire cycle of data acquisition, localization,
    and analysis. Commercial devices such as NanoSight and ZetaView provide a closed-solution to the problem. PyNTA aims
    at providing a superior approach, allowing researchers to have real-time information on the sample studied and a
    completely transparent approach regarding algorithms used.

    Nanospring tracking (NSTracking) is a special case of NTA in which partices are anchored to the surface and can be subject to
    both external oscillatory actuation and thermal diffusion.


    :last version: 18 March 2021 editted by Sanli Faez
    based on work by Aquiles Carattino <aquiles@uetke.com>
    :license: GPLv3, see LICENSE for more details
"""
import sys
import copy

import json
import os
import time
from threading import Event

from datetime import datetime

import h5py as h5py
import numpy as np
from multiprocessing import Queue, Process

from pynta import general_stop_event
from pynta.model.experiment.base_experiment import BaseExperiment
from pynta.model.experiment.nanospring_tracking.decorators import (check_camera,
                                                                     check_not_acquiring,
                                                                     make_async_thread)

from pynta.model.experiment.nanospring_tracking.localization import LocateParticles
from pynta.model.experiment.nanospring_tracking.saver import worker_listener
from pynta.model.experiment.nanospring_tracking.exceptions import StreamSavingRunning
from pynta.util import get_logger


from pynta.controller.devices.NIDAQ.ni_usb_6216 import NiUsb6216 as DaqController

import trackpy as tp

class DataPipeline:
    def __init__(self, callables_list = []) -> None:
        self.callables_list = callables_list
    
    def append_node(self, callable):
        self.callables_list.append(callable)
    
    def apply(self, data):
        for c in self.callables_list:
            # print("applying {} to {}".format(c, data))
            data = c(data)
            if data is None:
                return None
        return data
    
    def __call__(self, data):
        self.apply(data)

class ImageBuffer:
    def __init__(self, buffer = None) -> None:
        self.buffer = buffer
    def __call__(self, image):
        if self.buffer is None:
            # print("setting buffer as it was empty")
            self.buffer = np.copy(image)
        else:
            np.copyto(self.buffer, image, casting='no')
        return image

class Track:
    def __init__(self, diameter = 11) -> None:
        self.diameter = diameter
    def __call__(self, image):
        return tp.locate(image, self.diameter)

class ContinousTracker:
    def __init__(self, diameter = 11) -> None:
        self.diameter= diameter
        self.df = None
        self.first= True
    def __call__(self, img):
        if self.df is None:
            self.df = tp.locate(img, self.diameter)
        elif self.first:
            # self.first=False
            for index, row in self.df.iterrows():
                # img = img.transpose()
                y = row['x']
                x = row['y']
                rad = 2
                xmin = int(max(0, x - rad))
                xmax = int(min(x + rad, img.shape[0]))
                ymin = int(max(0, y - rad))
                ymax = int(min(y + rad, img.shape[1]))
                local = img[xmin:xmax, ymin:ymax]
                # print(local)
                amax = np.argmax(local, axis=None)
                # print(amax)
                x_, y_ = np.unravel_index(amax, local.shape)
                # print(np.max(local))
                # print("offsets are {}, {}".format(x_,y_))
                # Update the coordinate to the (new) location of the maximum
                #if local[(x_,y_)] > 1:
                row['x'] = ymin + y_ 
                row['y'] = xmin + x_ 
        return self.df

class SaveTracksToHDF5:
    def __init__(self, aqcuisition_grp):
        self.batching = 1024
        self.write_index = 0
        self.frame = 0

        self.grp = aqcuisition_grp.create_group("Tracks")
        #self.grp.attrs["diameter"] = self.diameter
        self.grp.attrs["creation"]  = str(datetime.utcnow())

        #self.locations_dataset = aqcuisition_grp.create_dataset("locations", shape=(8,self.batching), dtype=np.float32, maxshape=(8,None), chunks=(8, self.batching), compression='gzip')
        self.x_dataset = self.grp.create_dataset("x", shape=(self.batching,), dtype=np.float32, maxshape=(None,), chunks=(self.batching,))
        self.y_dataset = self.grp.create_dataset("y", shape=(self.batching,), dtype=np.float32, maxshape=(None,), chunks=(self.batching,))
        self.frame_dataset = self.grp.create_dataset("frames", shape=(self.batching,), dtype=np.uint64, maxshape=(None,), chunks=(self.batching,), compression='gzip')
        
    def __call__(self, locations):
        row_count = len(locations.index)
        #print("found {} particles on frame {}".format(row_count, self.frame))
        #todo: handle row_count > 
        old_size = self.x_dataset.shape[0]
        #print("old size is {}".format(old_size))
        while row_count + self.write_index > old_size:
            self.x_dataset.resize((old_size+self.batching,))
            self.y_dataset.resize((old_size+self.batching,))
            self.frame_dataset.resize((old_size+self.batching,))
            old_size += self.batching
        #print("trying to write x={}".format(locations["x"]))
        #print(locations["x"].shape)
        self.x_dataset[self.write_index:self.write_index+row_count] = locations["x"]
        self.y_dataset[self.write_index:self.write_index+row_count] = locations["y"]
        self.frame_dataset[self.write_index:self.write_index+row_count] = np.ones(row_count ,dtype= np.uint64)*self.frame
        self.write_index += row_count
        self.frame += 1
        return locations

class SaveImageToHDF5:
    def __init__(self, aqcuisition_grp, device, stride = 1):
        #self.dataset_writer = dataset_writer
        self.stride = stride-1
        self.counter = 0
        self.dataset_writer = aqcuisition_grp.create_dataset("Image", shape=(0,)+device.get_size(), dtype=device.data_type, maxshape=(None,)+device.get_size(), chunks=(1,)+device.get_size(), compression='gzip')
        self.dataset_writer.attrs["stride"] = stride
        self.dataset_writer.attrs["creation"]  = str(datetime.utcnow())
    def __call__(self, image):
        if self.counter == 0:
            # print("writting image to file..")
            #self.dataset_writer.send(image)
            dsize = self.dataset_writer.shape
            self.dataset_writer.resize((dsize[0]+1,) + dsize[1:])
            self.dataset_writer[-1,:] = image
        # else:
        #     print("Skipping image writting..")
        self.counter = self.counter + 1 if self.counter < self.stride else 0
        return image

class Batch:
    def __init__(self, number) -> None:
        self.number = number
        self.buffer = None
        self.index = 0
    def __call__(self, data):
        if self.buffer is None:
            self.buffer = np.zeros((self.number,)+data.shape, data.dtype)
        self.buffer[self.index,:] = data
        self.index += 1

class SaveDaqToHDF5:
    def __init__(self, aqcuisition_grp, device):
        #self.dataset_writer = dataset_writer
        self.counter = 0
        self.dataset_writer = aqcuisition_grp.create_dataset("DAQ-input", shape=(0,)+device.get_size(), dtype=device.data_type, maxshape=(None,)+device.get_size(), chunks=(1,)+device.get_size(), compression='gzip')
        # write out the signal generator settings.
        #self.dataset_writer.attrs["stride"] = stride
        self.dataset_writer.attrs["creation"]  = str(datetime.utcnow())
    def __call__(self, data):
        dsize = self.dataset_writer.shape
        self.dataset_writer.resize((dsize[0]+1,) + dsize[1:])
        self.dataset_writer[-1,:] = data
        return data

class FileWrangler:
    def __init__(self, filename) -> None:
        self.file = h5py.File(filename if filename.endswith('.hdf5') else filename + '.hdf5','w',  libver='latest')         
        self.file.attrs["creation"] = str(datetime.utcnow())
    
    def start_new_aquisition(self):
        #print("starting aq of {}".format(device))
        device_grp = self.file.require_group('data')
        aquisition_nr = len(device_grp.keys())
        grp = device_grp.create_group("Acquisition_{}".format(aquisition_nr))
        return grp

class Experiment(BaseExperiment):
    BACKGROUND_NO_CORRECTION = 0  # No background correction
    BACKGROUND_SINGLE_SNAP = 1

    def __init__(self, filename=None):
        #todo: camera is initialized using the config, DAQ is hardcoded.
        self.daq_controller = DaqController()
        self.camera = None  # This will hold the model for the camera
        self.current_height = None
        self.current_width = None
        self.max_width = None
        self.max_height = None
        super().__init__(filename)

        self.saving_location = False
        self.logger = get_logger(name=__name__)

        self.dropped_frames = 0
        self.keep_acquiring = True
        self.acquiring = False  # Status of the acquisition
        self.tracking = False

        self.monitoring_pixels = False
        self.monitor_callback = self.callback_pixel
        self.monitor_callback = self.callback_local_max_and_lock
        self.temp_monitor_values = {}

        
        
        self.background = np.array(())
        self.temp_image = None  # Temporary image, used to quickly have access to 'some' data and display it to the user
        self.tracked_locations = None
        self.movie_buffer = None  # Holds few frames of the movie in order to be able to do some analysis, save later, etc.
        self.last_index = 0  # Last index used for storing to the movie buffer
        self.stream_saving_running = False
        self.async_threads = []  # List holding all the threads spawn
        self.stream_saving_process = None
        self.link_particles_process = None
        self.calculate_histogram_process = None
        self.do_background_correction = False
        self.background_method = self.BACKGROUND_SINGLE_SNAP
        self.last_locations = None

        self.waterfall_index = 0

        self.locations_queue = Queue()
        self.tracks_queue = Queue()
        self.size_distribution_queue = Queue()
        self.saver_queue = Queue()
        self.keep_locating = True
        self._threads = []
        self._processes = []
        self._stop_free_run = Event()

        #self.location = LocateParticles(self.publisher, self.config['tracking'])
        self.fps = 0  # Calculates frames per second based on the number of frames received in a period of time
        # sys.excepthook = self.sysexcept  # This is very handy in case there are exceptions that force the program to quit.
        self.camera.configure(self.config['camera'])
        self.hdf5 = FileWrangler("output")
    def gui_file(self):
        return "electrophoretics"

    @check_camera  # Don't know yet if this is necessary???
    def add_monitor_coordinate(self, xy, label=None):
        """Add a minotor location. If label is None (default) the largest used integer + 1 will be used."""
        if not 'monitor_coordinates' in self.config:
            self.config['monitor_coordinates'] = {}
        if label is None:
            numbers_used = [k for k in self.config['monitor_coordinates'].keys() if isinstance(k, int)]
            label = 1 if not numbers_used else max(numbers_used)+1
        self.config['monitor_coordinates'][label] = xy
        self.monitoring_pixels = True
        # print('add_monitor', self.config['monitor_coordinates'])
        return label

    def clear_monitor_coordinates(self, label=None):
        """Specify specific label, of clear all by passing None (default)"""
        if not 'monitor_coordinates' in self.config or label is None:
            self.config['monitor_coordinates'] = {}
        elif label in self.config['monitor_coordinates']:
            del self.config['monitor_coordinates'][label]
        else:
            self.logger.warning("Coordinate not found")
        # If the list is empty, also stop analyzing the frames
        if self.config['monitor_coordinates'] == {}:
            self.monitoring_pixels = False

    def callback_pixel(self, img, coord):
        x, y = coord
        return img[int(x), int(y)]

    def callback_local_max_and_lock(self, img, coord):
        print("updating max")
        x, y = coord
        rad = 2
        xmin = int(max(0, x - rad))
        xmax = int(min(x + rad, img.shape[0]))
        ymin = int(max(0, y - rad))
        ymax = int(min(y + rad, img.shape[1]))
        local = img[xmin:xmax, ymin:ymax]
        x_, y_ = np.unravel_index(local.argmax(), local.shape)
        # Update the coordinate to the (new) location of the maximum
        coord[0] = xmin + x_
        coord[1] = ymin + y_
        return local[x_, y_]


    @check_camera
    @check_not_acquiring
    def snap_background(self):
        """ Snaps an image that will be stored as background.
        """
        self.logger.info('Acquiring background image')
        self.camera.configure(self.config['camera'])
        self.camera.set_acquisition_mode(self.camera.MODE_SINGLE_SHOT)
        # self.camera.trigger_camera()
        self.camera.start_acquisition()
        self.background = self.camera.read_camera()[-1]
        self.camera.stop_acquisition()
        self.logger.debug('Got an image of {} pixels'.format(self.backgound.shape))

    @check_camera
    @check_not_acquiring
    def set_roi(self, X, Y):
        """ Sets the region of interest of the camera, provided that the camera supports cropping. All the technicalities
        should be addressed on the camera model, not in this method.

        :param list X: horizontal position for the start and end of the cropping
        :param list Y: vertical position for the start and end of the cropping
        :raises ValueError: if either dimension of the cropping goes out of the camera total amount of pixels
        :returns: The final cropping dimensions, it may be that the camera limits the user desires
        """

        # self.logger.debug('Setting new camera ROI to x={},y={}'.format(X, Y))
        self.current_width, self.current_height = self.camera.set_ROI(X, Y)
        self.logger.debug('New camera width: {}px, height: {}px'.format(self.current_width, self.current_height))
        self.temp_image = None

    @check_camera
    @check_not_acquiring
    def clear_roi(self):
        """ Clears the region of interest and returns to the full frame of the camera.
        """
        self.logger.info('Clearing ROI settings')
        X = [0, self.max_width-1]
        Y = [0, self.max_height-1]
        self.camera.set_ROI(X, Y)

    @check_camera
    @check_not_acquiring
    @make_async_thread
    def snap(self):
        """ Snap a single frame.
        """
        self.logger.info('Snapping a picture')
        print("conbfigure..")
        # self.camera.configure(self.config['camera'])
        print("single shot...")
        self.camera.set_acquisition_mode(self.camera.MODE_SINGLE_SHOT)
        # self.camera.trigger_camera()
        # self.check_background()
        print("starting ot grab data")
        self.camera.start_acquisition()
        data = self.camera.read_camera()[-1]
        self.camera.stop_acquisition()
        # self.publisher.publish('snap', data)
        self.temp_image = data
        self.logger.debug('Got an image of {}x{} pixels'.format(self.temp_image.shape[0], self.temp_image.shape[1]))

    #@make_async_thread
    @check_not_acquiring
    @check_camera
    def start_free_run(self):
        """ Starts continuous acquisition from the camera, but it is not being saved. This method is the workhorse
        of the program. While this method runs on its own thread, it will broadcast the images to be consumed by other
        methods. In this way it is possible to continuously save to hard drive, track particles, etc.
        """
        return self.start_capture()
        # self.logger.info('Starting a free run')
        # self.camera.configure(self.config['camera'])
        # self.camera.set_acquisition_mode(self.camera.MODE_SINGLE_SHOT)
        # self.camera.trigger_camera()
        # self.check_background()
        # image = self.camera.read_camera()[-1]
        # locations = tp.locate(image, self.config['tracking']['locate']['diameter'])
        # self.clear_monitor_coordinates()
        # for _idx, row in locations.iterrows():
        #     self.add_monitor_coordinate((row['x'], row['y']))
        # self.temp_locations = locations
        # self.tracking = True
        # def update_tmp(df):
        #     self.temp_locations = df
        # pipeline = DataPipeline([ContinousTracker(self.config['tracking']['locate']['diameter']), update_tmp])
        # def fnc(data):
        #     self.temp_image = data[-1]
        #     for img in data:
        #         pipeline(img)

        # self.camera.start_free_run(fnc)

    def start_capture(self):
        self.logger.info('Starting a free run acquisition')
        # self.camera.configure(self.config['camera'])
        aqcuisition = self.hdf5.start_new_aquisition()
        def null(x):
            pass
        self.daq_controller.set_processing_function(SaveDaqToHDF5(aqcuisition, self.daq_controller))
        #self.daq_controller.set_processing_function(null)
        print("setting up for snap!")
        self.camera.set_acquisition_mode(self.camera.MODE_SINGLE_SHOT)
        self.camera.start_acquisition()
        # self.camera.trigger_camera()
        # self.check_background()
        image = self.camera.read_camera()[-1]
        self.camera.stop_acquisition()
        print("got first frame, locating now!")
        locations = tp.locate(image, self.config['tracking']['locate']['diameter'])
        self.clear_monitor_coordinates()
        # for _idx, row in locations.iterrows():
        x,y = self.camera.get_size()
        self.add_monitor_coordinate((x/2, y/2))
        # self.temp_locations = locations
        # self.tracking = True
        self.tracking = True
        def update_tmp(df):
            self.temp_locations = df
        print("created pipeline")
        # pipeline = DataPipeline([SaveImageToHDF5(aqcuisition, self.camera, 10),ContinousTracker(self.config['tracking']['locate']['diameter']), SaveTracksToHDF5(aqcuisition), update_tmp])
        pipeline = DataPipeline([SaveImageToHDF5(aqcuisition, self.camera, 4)])
        def fnc(data):
            # print("proccesing data!")
            if len(data) > 0:
                self.temp_image = data[-1][1]
            for img in data:
                pipeline(img[-1])
        print("calling start free run")
        self.camera.start_free_run(fnc)

    # @property
    # def temp_locations(self):
    #     return self.localize_particles_image(self.temp_image)

    def stop_free_run(self):
        """ Stops the free run by setting the ``_stop_event``. It is basically a convenience method to avoid
        having users dealing with somewhat lower level threading options.
        """
        self.logger.info('Stopping free-run')
        self.camera.stop_free_running()
        # self.camera.stop_acquisition()
        self.daq_controller.set_processing_function(lambda x: None)
        self.tracking = False

    def save_image(self):
        """ Saves the last acquired image. The file to which it is going to be saved is defined in the config.
        """
        if self.temp_image:
            self.logger.info('Saving last acquired image')
            # Data will be appended to existing file
            file_name = self.config['saving']['filename_photo'] + '.hdf5'
            file_dir = self.config['saving']['directory']
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
                self.logger.debug('Created directory {}'.format(file_dir))

            with h5py.File(os.path.join(file_dir, file_name), "a") as f:
                now = str(datetime.now())
                g = f.create_group(now)
                g.create_dataset('image', data=self.temp_image)
                g.create_dataset('metadata', data=json.dumps(self.config))
                f.flush()
            self.logger.debug('Saved image to {}'.format(os.path.join(file_dir, file_name)))
        else:
            self.logger.warning('Tried to save an image, but no image was acquired yet.')

    def save_stream(self):
        """ Saves the queue to a file continuously. This is an async function, that can be triggered before starting
        the stream. It relies on the multiprocess library. It uses a queue in order to get the data to be saved.
        In normal operation, it should be used together with ``add_to_stream_queue``.
        """
        if self.save_stream_running:
            self.logger.warning('Tried to start a new instance of save stream')
            raise StreamSavingRunning('You tried to start a new process for stream saving')

        self.logger.info('Starting to save the stream')
        file_name = self.config['saving']['filename_video'] + '.hdf5'
        file_dir = self.config['saving']['directory']
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
            self.logger.debug('Created directory {}'.format(file_dir))
        file_path = os.path.join(file_dir, file_name)
        max_memory = self.config['saving']['max_memory']

        self.stream_saving_process = Process(target=worker_listener,
                                             args=(file_path, json.dumps(self.config), 'free_run'),
                                             kwargs={'max_memory': max_memory})
        self.stream_saving_process.start()
        self.logger.debug('Started the stream saving process')

    def stop_save_stream(self):
        """ Stops saving the stream.
        """
        if self.save_stream_running:
            self.logger.info('Stopping the saving stream process')
            self.saver_queue.put('Exit')
            self.publisher.publish('free_run', 'stop')
            return
        self.logger.info('The saving stream is not running. Nothing will be done.')

    def start_tracking(self):
        """ Starts the tracking of the particles
        """
        self.tracking = True
        self.location.start_tracking('free_run')

    def stop_tracking(self):
        self.tracking = False
        self.location.stop_tracking()

    def start_saving_location(self):
        self.saving_location = True
        file_name = self.config['saving']['filename_tracks'] + '.hdf5'
        file_dir = self.config['saving']['directory']
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
            self.logger.debug('Created directory {}'.format(file_dir))
        file_path = os.path.join(file_dir, file_name)
        #self.location.start_saving(file_path, json.dumps(self.config))

    def stop_saving_location(self):
        self.saving_location = False
        #self.location.stop_saving()

    def localize_particles_image(self, image=None):
        """
        when complete should localize in the image based on a simple peak-finder

        """
        pass

    @property
    def save_stream_running(self):
        if self.stream_saving_process is not None:
            try:
                return self.stream_saving_process.is_alive()
            except:
                return False
        return False

    @property
    def link_particles_running(self):
        if self.link_particles_process is not None:
            try:
                return self.link_particles_process.is_alive()
            except:
                return False
        return False

    def stop_link_particles(self):
        """ Stops the linking process.
        """
        if self.link_particles_running:
            self.logger.info('Stopping the linking particles process')
            self.locations_queue.put('Exit')
            return
        self.logger.warning('The linking particles process is not running. Nothing will be done.')

    def empty_saver_queue(self):
        """ Empties the queue where the data from the movie is being stored.
        """
        if not self.saver_queue.empty():
            self.logger.info('Clearing the saver queue')
            self.logger.debug('Current saver queue length: {}'.format(self.saver_queue.qsize()))
            while not self.saver_queue.empty() or self.saver_queue.qsize() > 0:
                self.saver_queue.get()
            self.logger.debug('Saver queue cleared')

    def empty_locations_queue(self):
        """ Empties the queue with location data.
        """
        if not self.locations_queue.empty():
            self.logger.info('Location queue not empty. Cleaning.')
            self.logger.debug('Current location queue length: {}'.format(self.locations_queue.qsize()))
            while not self.locations_queue.empty():
                self.locations_queue.get()
            self.logger.debug('Location queue cleared')


    def check_background(self):
        """ Checks whether the background is set.
        """

        if self.do_background_correction:
            self.logger.info('Setting up the background corretion')
            if self.background_method == self.BACKGROUND_SINGLE_SNAP:
                self.logger.debug('Background single snap')
                if self.background is None or self.background.shape != [self.current_width, self.current_height]:
                    self.logger.warning('Background not set. Defaulting to no background...')
                    self.background = None
                    self.do_background_correction = False

    def finalize(self):
        general_stop_event.set()
        self.monitoring_pixels = False
        self.stop_free_run()
        time.sleep(.5)
        self.stop_save_stream()
        #self.location.finalize()
        self.camera.stop_free_running()
        super().finalize()

    def sysexcept(self, exc_type, exc_value, exc_traceback):
        self.logger.exception('Got an unhandled exception: {}'.format(exc_type))
        self.logger.exception('Traceback: {}'.format(exc_traceback))
        self.logger.exception('Value: {}'.format(exc_value))
        self.__exit__()
        sys.exit()

    def __enter__(self):
        super().__enter__()
        return self

    def __exit__(self, *args):
        self.empty_saver_queue()
        self.empty_locations_queue()

        if self.save_stream_running:
            self.logger.info('Stopping the saver process')
            self.stop_save_stream()

        if self.link_particles_running:
            self.stop_link_particles()

        self.stop_free_run()
        general_stop_event.set()
