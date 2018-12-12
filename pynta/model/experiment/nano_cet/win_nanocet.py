# -*- coding: utf-8 -*-
"""
    nano_cet.py
    ===========
    Capillary Electrokinetic Tracking of Nanoparticles (nanoCET) is a technique that allows to characterize very small
    objects thanks to calculating their diffusion properties inside a capillary. The main advantage of the technique
    is that objects remain in the Field of View for extended periods of time and thus their properties can be quantified
    with a high accuracy.


    :copyright:  Aquiles Carattino <aquiles@aquicarattino.com>
    :license: GPLv3, see LICENSE for more details
"""
import sys
import copy
import importlib
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
from pynta.model.experiment.nano_cet.decorators import (check_camera,
                                                        check_not_acquiring,
                                                        make_async_thread)

from pynta.model.experiment.nano_cet.localization import link_queue, calculate_locations_image, \
    calculate_histogram_sizes, LocateParticles

from pynta.model.experiment.nano_cet.saver import worker_listener
from pynta.model.experiment.nano_cet.exceptions import StreamSavingRunning
from pynta.util import get_logger
import trackpy as tp


class NanoCET(BaseExperiment):
    """ Experiment class for performing a nanoCET measurement."""
    BACKGROUND_NO_CORRECTION = 0  # No backround correction
    BACKGROUND_SINGLE_SNAP = 1

    def __init__(self, filename=None):
        super().__init__()
        self.free_run_running = False
        self.saving_location = False
        self.logger = get_logger(name=__name__)

        self.load_configuration(filename)

        self.dropped_frames = 0
        self.keep_acquiring = True
        self.acquiring = False  # Status of the acquisition
        self.tracking = False
        self.camera = None  # This will hold the model for the camera
        self.current_height = None
        self.current_width = None
        self.max_width = None
        self.max_height = None
        self.background = None
        self.temp_image = None  # Temporary image, used to quickly have access to 'some' data and display it to the user
        # self.temp_locations = None
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

        self.location = LocateParticles(self.publisher, self.config['tracking'])
        self.fps = 0  # Calculates frames per second based on the number of frames received in a period of time
        # sys.excepthook = self.sysexcept  # This is very handy in case there are exceptions that force the program to quit.

    def initialize_camera(self):
        """ Initializes the camera to be used to acquire data. The information on the camera should be provided in the
        configuration file and loaded with :meth:`~self.load_configuration`. It will load the camera assuming
        it is located in pynta/model/cameras/[model].

        .. todo:: Define how to load models from outside of pynta. E.g. from a user-specified folder.
        """
        try:
            self.logger.info('Importing camera model {}'.format(self.config['camera']['model']))
            self.logger.debug('pynta.model.cameras.' + self.config['camera']['model'])

            camera_model_to_import = 'pynta.model.cameras.' + self.config['camera']['model']
            cam_module = importlib.import_module(camera_model_to_import)
        except ModuleNotFoundError:
            self.logger.error('The model {} for the camera was not found'.format(self.config['camera']['model']))
            raise
        except:
            self.logger.exception('Unhandled exception')
            raise

        cam_init_arguments = self.config['camera']['init']

        if 'extra_args' in self.config['camera']:
            self.logger.info('Initializing camera with extra arguments')
            self.logger.debug('cam_module.camera({}, {})'.format(cam_init_arguments, self.config['camera']['extra_args']))
            self.camera = cam_module.camera(cam_init_arguments, *self.config['Camera']['extra_args'])
        else:
            self.logger.info('Initializing camera without extra arguments')
            self.logger.debug('cam_module.camera({})'.format(cam_init_arguments))
            self.camera = cam_module.camera(cam_init_arguments)

        self.camera.initializeCamera()
        self.current_width, self.current_height = self.camera.getSize()
        self.logger.info('Camera sensor ROI: {}px X {}px'.format(self.current_width, self.current_height))
        self.max_width = self.camera.GetCCDWidth()
        self.max_height = self.camera.GetCCDHeight()
        self.logger.info('Camera sensor size: {}px X {}px'.format(self.max_width, self.max_height))

    @check_camera
    @check_not_acquiring
    def snap_background(self):
        """ Snaps an image that will be stored as background.
        """
        self.logger.info('Acquiring background image')
        self.camera.configure(self.config['camera'])
        self.camera.setAcquisitionMode(self.camera.MODE_SINGLE_SHOT)
        self.camera.triggerCamera()
        self.background = self.camera.readCamera()[-1]
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

        self.logger.debug('Setting new camera ROI to x={},y={}'.format(X, Y))
        self.current_width, self.current_height = self.camera.setROI(X, Y)
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
        self.camera.setROI(X, Y)

    @check_camera
    @check_not_acquiring
    @make_async_thread
    def snap(self):
        """ Snap a single frame. It is not an asynchronous method. To make it async, it should be placed within
        a different thread.
        """
        self.logger.info('Snapping a picture')
        self.camera.configure(self.config['camera'])
        self.camera.setAcquisitionMode(self.camera.MODE_SINGLE_SHOT)
        self.camera.triggerCamera()
        self.check_background()
        data = self.camera.readCamera()[-1]
        self.publisher.publish('snap', data)
        self.temp_image = data
        self.logger.debug('Got an image of {}x{} pixels'.format(self.temp_image.shape[0], self.temp_image.shape[1]))

    @make_async_thread
    @check_not_acquiring
    @check_camera
    def start_free_run(self):
        """ Starts continuous acquisition from the camera, but it is not being saved. This method is the workhorse
        of the program. While this method runs in its thread, it will broadcast the images to be consumed by other
        methods. In this way it is possible to continuously save to hard drive, track particles, etc.
        """

        self.logger.info('Starting a free run acquisition')
        first = True
        i = 0  # Used to keep track of the number of frames
        self.camera.configure(self.config['camera'])
        self._stop_free_run.clear()
        t0 = time.time()
        self.free_run_running = True
        while not self._stop_free_run.is_set():
            if first:
                self.logger.debug('First frame of a free_run')
                self.camera.setAcquisitionMode(self.camera.MODE_CONTINUOUS)
                self.camera.triggerCamera()  # Triggers the camera only once
                first = False

            data = self.camera.readCamera()
            self.logger.debug('Got {} new frames'.format(len(data)))
            for img in data:
                i += 1
                self.logger.debug('Number of frames: {}'.format(i))
                if self.do_background_correction and self.background_method == self.BACKGROUND_SINGLE_SNAP:
                    img -= self.background

                # This will broadcast the data just acquired with the current timestamp
                # The timestamp is very unreliable, especially if the camera has a frame grabber.
                self.publisher.publish('free_run', [time.time(), img])
            self.fps = round(i / (time.time() - t0))
            self.temp_image = data[-1]
        self.free_run_running = False
        self.camera.stopAcq()

    @property
    def temp_locations(self):
        return self.localize_particles_image(self.temp_image)

    def stop_free_run(self):
        """ Stops the free run by setting the ``_stop_event``. It is basically a convenience method to avoid
        having users dealing with somewhat lower level threading options.
        """
        self.logger.info('Setting the stop_event')
        self._stop_free_run.set()

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

    def link_particles(self):
        """ Starts linking the particles while the acquisition is in progress.
        """
        self.logger.info('Starting to link particles')
        self.link_particles_process = Process(target=link_queue, args=[self.locations_queue, self.publisher._queue,
                                                                       self.tracks_queue],
                                              kwargs=self.config['tracking']['link'])
        self.link_particles_process.start()
        self.logger.debug('Started the linking process')

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
        self.location.start_saving(file_path, json.dumps(self.config))

    def stop_saving_location(self):
        self.saving_location = False
        self.location.stop_saving()

    def start_linking_locations(self):
        self.logger.debug('Start linking locations')
        self.location.start_linking()

    def stop_linking_locations(self):
        self.logger.debug('Stop linking locations')
        self.location.stop_linking()

    def localize_particles_image(self, image=None):
        """
        Localizes particles based on trackpy. It is a convenience function in order to use the configuration parameters
        instead of manually passing them to trackpy.

        """
        if image is None:
            image = self.temp_image

        params = copy.copy(self.config['tracking']['locate'])
        diameter = params.pop('diameter')
        return tp.locate(image, diameter, **params)

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

    def calculate_waterfall(self, image):
        """ A waterfall is the product of summing together all the vertical values of an image and displaying them
        as lines on a 2D image. It is how spectrometers normally work. A waterfall can be produced either by binning the
        image in the vertical direction directly at the camera, or by doing it in software.
        The first has the advantage of speeding up the readout process. The latter has the advantage of working with any
        camera.
        This method will work either with 1D arrays or with 2D arrays and will generate a stack of lines.
        """

        if self.waterfall_index == self.config['waterfall']['length_waterfall']:
            self.waterfall_data = np.zeros((self.config['waterfall']['length_waterfall'], self.camera.width))
            self.waterfall_index = 0

        center_pixel = np.int(self.camera.height / 2)   # Calculates the center of the image
        vbinhalf = np.int(self.config['waterfall']['vertical_bin'])
        if vbinhalf >= self.current_height / 2 - 1:
            wf = np.array([np.sum(image, 1)])
        else:
            wf = np.array([np.sum(image[:, center_pixel - vbinhalf:center_pixel + vbinhalf], 1)])
        self.waterfall_data[self.waterfall_index, :] = wf
        self.waterfall_index += 1
        self.publisher.publish('waterfall_data', wf)

    def check_background(self):
        """ Checks whether the background is set.
        """

        if self.do_background_correction:
            self.logger.info('Setting up the background corretion')
            if self.background_method == self.BACKGROUND_SINGLE_SNAP:
                self.logger.debug('Bacground single snap')
                if self.background is None or self.background.shape != [self.current_width, self.current_height]:
                    self.logger.warning('Background not set. Defaulting to no background...')
                    self.background = None
                    self.do_background_correction = False

    def finalize(self):
        general_stop_event.set()
        self.stop_free_run()
        time.sleep(.5)
        self.stop_save_stream()
        self.location.finalize()
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

        # super().__exit__(*args)

