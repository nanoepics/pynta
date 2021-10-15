# -*- coding: utf-8 -*-
"""

"""
import sys
import copy

import json
import os
import time
# from threading import Event

from datetime import datetime

import h5py as h5py
import numpy as np
# from multiprocessing import Queue, Process

from pynta import general_stop_event
from pynta.model.experiment.base_experiment import BaseExperiment
# from pynta.model.experiment.nanospring_tracking.decorators import (check_camera,
#                                                                      check_not_acquiring,
#                                                                      make_async_thread)

# from pynta.model.experiment.nanospring_tracking.localization import LocateParticles
# from pynta.model.experiment.nanospring_tracking.saver import worker_listener
# from pynta.model.experiment.nanospring_tracking.exceptions import StreamSavingRunning
from pynta.util import get_logger
from pynta import Q_

from pynta.controller.devices.NIDAQ.ni_usb_6216 import NiUsb6216 as DaqController

# import trackpy as tp
from scipy import ndimage
from pynta_drivers import Camera as NativeCamera;


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
    def __init__(self, to_track) -> None:
        self.to_track = to_track
    def __call__(self, img):
        for i in range(0, len(self.to_track[0])):
            x = self.to_track[0][i]
            y = self.to_track[1][i]
            rad = 30
            xmin = int(max(0, x - rad))
            xmax = int(min(x + rad, img.shape[1]))
            ymin = int(max(0, y - rad))
            ymax = int(min(y + rad, img.shape[0]))
            # print("{}, {} in image of size {}".format(x,y,img.shape))
            local = img[ymin:ymax, xmin:xmax]
            # print(local)
            amax = np.argmax(local, axis=None)
            # print(amax)
            y_, x_ = np.unravel_index(amax, local.shape)
            # print("offsets are {}, {}, position {}, {}, intenity {}".format(x_,y_, x, y, np.max(local)))
            # Update the coordinate to the (new) location of the maximum
            #if local[(x_,y_)] > 1:
            self.to_track[1][i] = ymin + y_ 
            self.to_track[0][i] = xmin + x_ 
        return self.to_track

class ContinousTracker2:
    def __init__(self, to_track) -> None:
        self.to_track = to_track
    def __call__(self, img):
        for i in range(0, len(self.to_track[0])):
            x = self.to_track[0][i]
            y = self.to_track[1][i]
            rad = 16
            xmin = int(max(0, x - rad))
            xmax = int(min(x + rad, img.shape[1]))
            ymin = int(max(0, y - rad))
            ymax = int(min(y + rad, img.shape[0]))
            # print("{}, {} in image of size {}".format(x,y,img.shape))
            local = img[ymin:ymax, xmin:xmax]
            if local.sum() > 0:
                (y,x) = ndimage.measurements.center_of_mass(local)
                print("offsets are {}, {}, intenity {}".format(rad-x-0.5,rad-y-0.5,np.max(local)))
                self.to_track[1][i] -= rad-y-0.5
                self.to_track[0][i] -= rad-x-0.5
                self.to_track[2][i] = np.mean(local)
        return self.to_track

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
        self.i_dataset = self.grp.create_dataset("intensities", shape=(self.batching,), dtype=np.float32, maxshape=(None,), chunks=(self.batching,))
        self.frame_dataset = self.grp.create_dataset("frames", shape=(self.batching,), dtype=np.uint64, maxshape=(None,), chunks=(self.batching,), compression='gzip')
        
    def __call__(self, locations):
        row_count = len(locations[0])
        if row_count:
            #print("found {} particles on frame {}".format(row_count, self.frame))
            #todo: handle row_count > 
            old_size = self.x_dataset.shape[0]
            #print("old size is {}".format(old_size))
            while row_count + self.write_index > old_size:
                self.x_dataset.resize((old_size+self.batching,))
                self.y_dataset.resize((old_size+self.batching,))
                self.i_dataset.resize((old_size+self.batching,))
                self.frame_dataset.resize((old_size+self.batching,))
                old_size += self.batching
            #print("trying to write x={}".format(locations["x"]))
            #print(locations["x"].shape)
            self.x_dataset[self.write_index:self.write_index+row_count] = locations[0]
            self.y_dataset[self.write_index:self.write_index+row_count] = locations[1]
            self.i_dataset[self.write_index:self.write_index+row_count] = locations[2]
            self.frame_dataset[self.write_index:self.write_index+row_count] = np.ones(row_count ,dtype= np.uint64)*self.frame
            self.write_index += row_count
        self.frame += 1
        return locations

class SaveImageToHDF5:
    def __init__(self, aqcuisition_grp, device, stride = 1):
        #self.dataset_writer = dataset_writer
        self.stride = stride-1
        self.counter = 0
        size = tuple(device.get_size())
        self.dataset_writer = aqcuisition_grp.create_dataset("Image", shape=(0,)+size, dtype=np.uint16, maxshape=(None,)+size, chunks=(1,)+size, compression='gzip')
        self.dataset_writer.attrs["stride"] = stride
        self.dataset_writer.attrs["creation"]  = str(datetime.utcnow())
    def __call__(self, image):
        if self.counter == 0:
            # print("writting image to file..")
            #self.dataset_writer.send(image)
            dsize = self.dataset_writer.shape
            self.dataset_writer.resize((dsize[0]+1,) + image.shape)
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
        self.config = {}  # Dictionary storing the configuration of the experiment
        self.logger = get_logger(name=__name__)
        self.load_configuration(filename)        
        self.camera = NativeCamera(self.config["camera"]['model'])  # This will hold the model for the camera
        self.camera.set_roi([int(self.config["camera"]["roi_x1"]), int(self.config["camera"]["roi_x2"])], [int(self.config["camera"]["roi_y1"]), int(self.config["camera"]["roi_y2"])])
        self.camera.set_exposure(float(Q_(self.config["camera"]["exposure_time"]).m_as("seconds")))
        self.daq_controller = DaqController()
        # self.current_height = None
        # self.current_width = None
        # self.max_width = None
        # self.max_height = None
        super().__init__(filename)
        self.temp_image = None
        self.tracked_locations = ([],[],[])
        self.hdf5 = FileWrangler("output")

    def gui_file(self):
        return "testing"

    def set_roi(self, X, Y):
        """ Sets the region of interest of the camera, provided that the camera supports cropping. All the technicalities
        should be addressed on the camera model, not in this method.

        :param list X: horizontal position for the start and end of the cropping
        :param list Y: vertical position for the start and end of the cropping
        :raises ValueError: if either dimension of the cropping goes out of the camera total amount of pixels
        :returns: The final cropping dimensions, it may be that the camera limits the user desires
        """

        # self.logger.debug('Setting new camera ROI to x={},y={}'.format(X, Y))
        self.camera.set_roi(X, Y)
        self.current_width, self.current_height = self.camera.get_size()
        self.logger.debug('New camera width: {}px, height: {}px'.format(self.current_width, self.current_height))
        self.temp_image = np.zeros((self.current_width, self.current_height), dtype=np.uint16)

    def clear_roi(self):
        """ Clears the region of interest and returns to the full frame of the camera.
        """
        self.logger.info('Clearing ROI settings')
        X = [0, self.max_width]
        Y = [0, self.max_height]
        self.set_roi(X, Y)

    # @make_async_thread
    def snap(self):
        """ Snap a single frame.
        """
        img = np.zeros(self.camera.get_size(), dtype=np.uint16, order='C')
        self.camera.snap_into(img)
        self.temp_image = img

    #@make_async_thread
    # @check_not_acquiring
    # @check_camera
    def start_free_run(self):
        """ Starts continuous acquisition from the camera, but it is not being saved. This method is the workhorse
        of the program. While this method runs on its own thread, it will broadcast the images to be consumed by other
        methods. In this way it is possible to continuously save to hard drive, track particles, etc.
        """
        return self.start_capture()

    def start_capture(self):
    #   self.camera.stream_into(self.temp_image)
        aqcuisition = self.hdf5.start_new_aquisition()
        self.daq_controller.set_processing_function(SaveDaqToHDF5(aqcuisition, self.daq_controller))
        def update_img(img):
            # print("updating temp image to ", img)
            self.temp_image = img
            return img
        # self.tracking = True
        # self.tracking = False
        # def update_trck(df):
        #     self.tracked_locations = df
        #     return df
        pipeline = DataPipeline([SaveImageToHDF5(aqcuisition, self.camera, 10),update_img, ContinousTracker2(self.tracked_locations), SaveTracksToHDF5(aqcuisition)])
        x, y = self.camera.get_size()
        bytes_per_frame = x*y*2
        bytes_to_buffer = 1024*1024*128
        self.camera.start_stream(int(bytes_to_buffer/bytes_per_frame), pipeline)

    # @property
    # def temp_locations(self):
    #     return self.localize_particles_image(self.temp_image)

    def stop_free_run(self):
        """ Stops the free run by setting the ``_stop_event``. It is basically a convenience method to avoid
        having users dealing with somewhat lower level threading options.
        """
        self.daq_controller.set_processing_function(lambda x: None)
        self.camera.stop_stream()
        print("stream stopped in python!")

    def save_image(self):
        """ Saves the last acquired image. The file to which it is going to be saved is defined in the config.
        """
        # if self.temp_image:
        #     self.logger.info('Saving last acquired image')
        #     # Data will be appended to existing file
        #     file_name = self.config['saving']['filename_photo'] + '.hdf5'
        #     file_dir = self.config['saving']['directory']
        #     if not os.path.exists(file_dir):
        #         os.makedirs(file_dir)
        #         self.logger.debug('Created directory {}'.format(file_dir))

        #     with h5py.File(os.path.join(file_dir, file_name), "a") as f:
        #         now = str(datetime.now())
        #         g = f.create_group(now)
        #         g.create_dataset('image', data=self.temp_image)
        #         g.create_dataset('metadata', data=json.dumps(self.config))
        #         f.flush()
        #     self.logger.debug('Saved image to {}'.format(os.path.join(file_dir, file_name)))
        # else:
        #     self.logger.warning('Tried to save an image, but no image was acquired yet.')

    def add_monitor_coordinate(self, coord):
        self.tracked_locations[0].append(coord[0])
        self.tracked_locations[1].append(coord[1])
        self.tracked_locations[2].append(0.0)
    def clear_monitor_coordinates(self):
        self.tracked_locations[0].clear()
        self.tracked_locations[1].clear()
        self.tracked_locations[2].clear()

    def save_stream(self):
        """ Saves the queue to a file continuously. This is an async function, that can be triggered before starting
        the stream. It relies on the multiprocess library. It uses a queue in order to get the data to be saved.
        In normal operation, it should be used together with ``add_to_stream_queue``.
        """
        # if self.save_stream_running:
        #     self.logger.warning('Tried to start a new instance of save stream')
        #     raise StreamSavingRunning('You tried to start a new process for stream saving')

        # self.logger.info('Starting to save the stream')
        # file_name = self.config['saving']['filename_video'] + '.hdf5'
        # file_dir = self.config['saving']['directory']
        # if not os.path.exists(file_dir):
        #     os.makedirs(file_dir)
        #     self.logger.debug('Created directory {}'.format(file_dir))
        # file_path = os.path.join(file_dir, file_name)
        # max_memory = self.config['saving']['max_memory']

        # self.stream_saving_process = Process(target=worker_listener,
        #                                      args=(file_path, json.dumps(self.config), 'free_run'),
        #                                      kwargs={'max_memory': max_memory})
        # self.stream_saving_process.start()
        # self.logger.debug('Started the stream saving process')

    def stop_save_stream(self):
        """ Stops saving the stream.
        """
        # if self.save_stream_running:
        #     self.logger.info('Stopping the saving stream process')
        #     self.saver_queue.put('Exit')
        #     self.publisher.publish('free_run', 'stop')
        #     return
        # self.logger.info('The saving stream is not running. Nothing will be done.')

    def start_tracking(self):
        """ Starts the tracking of the particles
        """
        # self.tracking = True
        # self.location.start_tracking('free_run')

    def stop_tracking(self):
        pass
        # self.tracking = False
        # self.location.stop_tracking()

    def start_saving_location(self):
        pass
        # self.saving_location = True
        # file_name = self.config['saving']['filename_tracks'] + '.hdf5'
        # file_dir = self.config['saving']['directory']
        # if not os.path.exists(file_dir):
        #     os.makedirs(file_dir)
        #     self.logger.debug('Created directory {}'.format(file_dir))
        # file_path = os.path.join(file_dir, file_name)
        #self.location.start_saving(file_path, json.dumps(self.config))

    def stop_saving_location(self):
        pass
        # self.saving_location = False
        #self.location.stop_saving()

    def localize_particles_image(self, image=None):
        """
        when complete should localize in the image based on a simple peak-finder

        """
        pass

    @property
    def save_stream_running(self):
        # if self.stream_saving_process is not None:
        #     try:
        #         return self.stream_saving_process.is_alive()
        #     except:
        #         return False
        return False

    @property
    def link_particles_running(self):
        # if self.link_particles_process is not None:
        #     try:
        #         return self.link_particles_process.is_alive()
        #     except:
        #         return False
        return False

    def stop_link_particles(self):
        """ Stops the linking process.
        """
        # if self.link_particles_running:
        #     self.logger.info('Stopping the linking particles process')
        #     self.locations_queue.put('Exit')
        #     return
        self.logger.warning('The linking particles process is not running. Nothing will be done.')

    def empty_saver_queue(self):
        """ Empties the queue where the data from the movie is being stored.
        """
        # if not self.saver_queue.empty():
        #     self.logger.info('Clearing the saver queue')
        #     self.logger.debug('Current saver queue length: {}'.format(self.saver_queue.qsize()))
        #     while not self.saver_queue.empty() or self.saver_queue.qsize() > 0:
        #         self.saver_queue.get()
        #     self.logger.debug('Saver queue cleared')

    def empty_locations_queue(self):
        """ Empties the queue with location data.
        """
        # if not self.locations_queue.empty():
        #     self.logger.info('Location queue not empty. Cleaning.')
        #     self.logger.debug('Current location queue length: {}'.format(self.locations_queue.qsize()))
        #     while not self.locations_queue.empty():
        #         self.locations_queue.get()
        #     self.logger.debug('Location queue cleared')


    def check_background(self):
        """ Checks whether the background is set.
        """

        # if self.do_background_correction:
        #     self.logger.info('Setting up the background corretion')
        #     if self.background_method == self.BACKGROUND_SINGLE_SNAP:
        #         self.logger.debug('Background single snap')
        #         if self.background is None or self.background.shape != [self.current_width, self.current_height]:
        #             self.logger.warning('Background not set. Defaulting to no background...')
        #             self.background = None
        #             self.do_background_correction = False

    def finalize(self):
        # general_stop_event.set()
        # self.monitoring_pixels = False
        # self.stop_free_run()
        # time.sleep(.5)
        # self.stop_save_stream()
        #self.location.finalize()
        self.camera.stop_stream()
        super().finalize()

    def sysexcept(self, exc_type, exc_value, exc_traceback):
        self.logger.exception('Got an unhandled exception: {}'.format(exc_type))
        self.logger.exception('Traceback: {}'.format(exc_traceback))
        self.logger.exception('Value: {}'.format(exc_value))
        self.__exit__()
        sys.exit()
