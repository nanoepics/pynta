# -*- coding: utf-8 -*-
"""

ONGOING ISSUES:
- snap() doesn't work
- run measurment functionality doesn't update GUI and breaks "monitor mode" (threading?)
  We need to think about how we want to use the software:
  - what operating with human interaction
  - what operating "scripted"
  - which things to visualise
  - how to store all of this


DONE:
- change settings in pynta (like exposure time)
- click and zoom to fixed size (config defined), and a return to fullscreen button
- separate live view from saving
  through modification of pipeline
- LIVE REGION OF INTEREST UPDATING


NEXT TIME:
- test saving with real camera, because dummy caused errors

TODO:
- change tracking marker from standard cross to box of actual size that is used (i.e. (rad*2+1) by (rad*2+1) )
- single snapshot option: HOW TO SAVE?
- live graph of image analysis data (see pyocv version), but not scrolling, but oscilloscope style
- daq settings in config (maybe also keep a gui)
- perhaps it would be nice to show a crosshair when camera is primed to click (add point / zoom)
- ...

SUGGESTION:
- button: toggle live view on/off   DONE FOR stream and save stream, but not yet for tracking
- button: toggle save (part of) frames to file
- ? live image analysis
- button: toggle save live image analysis


"""
import sys
# from threading import Event



# from multiprocessing import Queue, Process
import time

from PyQt5.QtTest import QTest   # use QTest.qWait(ms) as a sleep that doesn't freeze the GUI

import pynta
from pynta import general_stop_event
from pynta.model.experiment.base_experiment import *
import numpy as np
# from multiprocessing import Queue, Process
import pynta
from pynta import general_stop_event
from pynta.model.experiment.base_experiment import BaseExperiment, DataPipeline, SaveTracksToHDF5, SaveImageToHDF5, SaveDaqToHDF5, SaveTriggerToHDF5, FileWrangler
# from pynta.model.experiment.nanospring_tracking.decorators import (check_camera,
#                                                                      check_not_acquiring,
#                                                                      make_async_thread)

# from pynta.model.experiment.nanospring_tracking.localization import LocateParticles
# from pynta.model.experiment.nanospring_tracking.saver import worker_listener
# from pynta.model.experiment.nanospring_tracking.exceptions import StreamSavingRunning
from pynta.util import get_logger
from pynta import Q_

from pynta.controller.devices.NIDAQ.ni_usb_6216 import NiUsb6216 as DaqController
from pynta.controller.devices.NIDAQ.ni_usb_6216 import DummyNiUsb6216 as DaqController


# import trackpy as tp
from scipy import ndimage
from pynta_drivers import Camera as NativeCamera;


# class ContinousTracker:
#     def __init__(self, to_track) -> None:
#         self.to_track = to_track
#     def __call__(self, img):
#         for i in range(0, len(self.to_track[0])):
#             x = self.to_track[0][i]
#             y = self.to_track[1][i]
#             rad = 30
#             xmin = int(max(0, x - rad))
#             xmax = int(min(x + rad, img.shape[1]))
#             ymin = int(max(0, y - rad))
#             ymax = int(min(y + rad, img.shape[0]))
#             # print("{}, {} in image of size {}".format(x,y,img.shape))
#             local = img[ymin:ymax, xmin:xmax]
#             # print(local)
#             amax = np.argmax(local, axis=None)
#             # print(amax)
#             y_, x_ = np.unravel_index(amax, local.shape)
#             # print("offsets are {}, {}, position {}, {}, intenity {}".format(x_,y_, x, y, np.max(local)))
#             # Update the coordinate to the (new) location of the maximum
#             #if local[(x_,y_)] > 1:
#             self.to_track[1][i] = ymin + y_
#             self.to_track[0][i] = xmin + x_
#         return self.to_track

class ContinousTracker2:
    def __init__(self, to_track, rad=32) -> None:
        self.to_track = to_track
        self.rad = rad
        self.logger = get_logger(__name__)
        self.reduce_logging_frequency = 50
        self._reduce_logging_frequency = self.reduce_logging_frequency

    def __call__(self, img):
        for i in range(0, len(self.to_track[0])):
            x = self.to_track[0][i]
            y = self.to_track[1][i]
            xmin = int(max(0, x - self.rad))
            xmax = int(min(x + self.rad, img.shape[1]))
            ymin = int(max(0, y - self.rad))
            ymax = int(min(y + self.rad, img.shape[0]))
            self._reduce_logging_frequency -= 1
            if self._reduce_logging_frequency == 0:
                self.logger.debug("{}, {} in image of size {}".format(x,y,img.shape))
                self._reduce_logging_frequency = self.reduce_logging_frequency
            local = img[ymin:ymax, xmin:xmax]

            if local.sum() > 0:
                (y,x) = ndimage.measurements.center_of_mass(local)
                # self.logger.debug("offsets are {}, {}, sum intensity {}".format(self.rad-x-0.5, self.rad-y-0.5, np.sum(local)))
                self.to_track[1][i] -= self.rad-y-0.5
                self.to_track[0][i] -= self.rad-x-0.5
                self.to_track[2][i] = np.sum(local)
        return self.to_track


class Experiment(BaseExperiment):
    BACKGROUND_NO_CORRECTION = 0  # No background correction
    BACKGROUND_SINGLE_SNAP = 1

    def __init__(self, filename=None):
        self.config = {}  # Dictionary storing the configuration of the experiment
        self.logger = get_logger(name=__name__)
        # self.logger.setLevel(10)
        self.load_configuration(filename)
        self.camera = NativeCamera(self.config["camera"]['model'])  # This will hold the model for the camera
        self.camera.set_output_trigger()
        self.bg_correction = 0
        self._show_snap = False
        # ham = self.camera.as_hamamatsu()
        # ham.set_prop(....);

        self.camera.set_roi([int(self.config["camera"]["roi_x1"]), int(self.config["camera"]["roi_x2"])], [int(self.config["camera"]["roi_y1"]), int(self.config["camera"]["roi_y2"])])
        self.camera.set_exposure(float(Q_(self.config["camera"]["exposure_time"]).m_as("seconds")))
        self.daq_controller = DaqController()
        # self.current_height = None
        # self.current_width = None
        # self.max_width = None
        # self.max_height = None
        super().__init__(filename)
        self.save_image_object = None
        self.tracked_locations = ([],[],[])
        self.save_path = self.config.get('saving', {}).get('directory', '')
        if not os.path.exists(self.save_path):
            self.logger.warning('save directory does not exist, falling back to parent directory')
            self.save_path = pynta.parent_path
        save_name = self.config.get('saving', {}).get('filename_tracks', 'output')
        filename = os.path.join(self.save_path, save_name)
        self.hdf5 = FileWrangler(filename, meta_data={'example': 'file meta'})
        self._pipeline = DataPipeline(self)
        self.snap()
        self.snap_number = 0
        # self.temp_image = None
        # self.snap_image = None
        self.bg_image = self.snap_image

        self.measurement_methods = {'Example measurement method': self.my_measurement,
                                    }

    def my_measurement(self):
        # self.config['measurements']['a']
        self.logger.info('do awesome measurement')
        if not self.hdf5.is_closed:
            self.hdf5.close()
        self._pipeline = DataPipeline(self)
        filename = os.path.join(self.save_path, 'a')
        self.hdf5 = FileWrangler(filename)
        self.start_free_run()
        self.save_stream()
        for k in range(20):
            time.sleep(0.2)
            print(self.temp_image[90,90])
        self.stop_save_stream()
        self.stop_free_run()
        self.hdf5.close()


    # def bg_video(self):
    #     """This is redundant. This can now be done by Snap (and setting camera:snap_avg_N_frames in the config"""
    #     bg_correction_state = self.bg_correction
    #     self.bg_correction = False
    #     if self.camera.is_streaming:
    #         self.stop_free_run()
    #     x, y = self.camera.get_size()
    #     bytes_per_frame = x*y*2
    #     bytes_to_buffer = 1024*1024*128
    #     bg_array = []
    #     def process_img(arr):
    #         bg_array.append(arr)
    #         self.temp_image = arr
    #     self.camera.start_stream(int(bytes_to_buffer/bytes_per_frame), process_img)
    #     t0 = time.time() ######try QtTest.QTest.qWait(msecs)
    #     while time.time() < t0 + 2:
    #         pass
    #     self.camera.stop_stream()
    #     bg_array = np.array(bg_array)
    #     self.bg_image = bg_array.mean(axis=0).astype(np.int16)
    #     self.snap_image = self.bg_image
    #     self.bg_correction = bg_correction_state

    def update_config(self, **kwargs):
        old_camera_conf = self.config['camera'].copy()
        self.logger.info('Updating config')
        self.logger.debug('Config params: {}'.format(kwargs))
        self.config.update(**kwargs)
        if self.config['camera'] != old_camera_conf:
            self.camera.set_roi([int(self.config["camera"]["roi_x1"]), int(self.config["camera"]["roi_x2"])],
                                [int(self.config["camera"]["roi_y1"]), int(self.config["camera"]["roi_y2"])])
            self.camera.set_exposure(float(Q_(self.config["camera"]["exposure_time"]).m_as("seconds")))

    def gui_file(self):
        return "testing"

    def set_zoom(self, coords):
        """
        Sets ROI to area around cursor. Size determined in config.
        Takes care of region exceeding camera frame by moving area inside.
        """
        x, y = coords
        x = min(int(x), self.max_width - self.config['camera']['zoom_width']//2)
        left = max(0, x - self.config['camera']['zoom_width']//2)
        right = min(self.max_width, left + self.config['camera']['zoom_width'])
        y = min(int(y), self.max_height - self.config['camera']['zoom_height'] // 2)
        top = max(0, y - self.config['camera']['zoom_height'] // 2)
        bottom = min(self.max_height, top + self.config['camera']['zoom_height'])
        self.logger.info("Zooming ROI to {}, {}, {}, {}".format(left, right, top, bottom))
        self.set_roi([left, right], [top, bottom])

    def set_roi(self, X, Y):
        # PERHAPS WE NEED TO DISABLE THIS WHILE ALSO CAPTURING
        """ Sets the region of interest of the camera, provided that the camera supports cropping. All the technicalities
        should be addressed on the camera model, not in this method.

        :param list X: horizontal position for the start and end of the cropping
        :param list Y: vertical position for the start and end of the cropping
        :raises ValueError: if either dimension of the cropping goes out of the camera total amount of pixels
        :returns: The final cropping dimensions, it may be that the camera limits the user desires
        """

        # self.logger.debug('Setting new camera ROI to x={},y={}'.format(X, Y))
        was_running = self.camera.is_streaming()
        if was_running:
            self.stop_free_run()
        self.camera.set_roi(X, Y)
        self.current_width, self.current_height = self.camera.get_size()
        self.logger.debug('New camera width: {}px, height: {}px'.format(self.current_width, self.current_height))
        self.temp_image = np.zeros((self.current_width, self.current_height), dtype=np.uint16)
        self.config['camera']['roi_x1'] = int(X[0])
        self.config['camera']['roi_x2'] = int(X[1])
        self.config['camera']['roi_y1'] = int(Y[0])
        self.config['camera']['roi_y2'] = int(Y[1])
        if was_running:
            self.start_free_run()


    def clear_roi(self):
        """ Clears the region of interest and returns to the full frame of the camera.
        """
        self.logger.info('Clearing ROI settings')
        X = [0, self.max_width]
        Y = [0, self.max_height]
        self.set_roi(X, Y)

        # @make_async_thread

    def BG_from_snap(self, state=True):
        # UNDER CONSTRUCTION
        """
        Sets the current snap as bg_array and enables bg reduction.
        To disable bg reduction, pass state=False argument.

        It will save the BG file as a separate array in the file: backgound_##. With the same number as the Snap.


        """
        pass

    def snap(self):
        """
        New implementation of snap.
        It uses the continuous acquisition mode to avoid some buffer error in the rust code (when snap is called after a callback function has been "attached")
        It actually averages over several images. The amount is set in the config   camera: snap_avg_N_frames
        # When the camera is not acquiring yet, it runs it briefly.
        # If the camera is already acquiring, it replaces the save_img function of the pipeline briefly with one that stores the images.
        If the camera is already acquiring, it won't run
        """
        if self.camera.is_streaming():
            self.logger.warning('Stop live view before starting "snap acquisition"')
            return
        N = self.config['camera']['snap_avg_N_frames']
        if N <= 1:
            self.logger.info('Snap')
            img = np.zeros(self.camera.get_size(), dtype=np.uint16, order='C')
            self.camera.snap_into(img)
            self.snap_image = img.astype(np.int16)
            self.temp_image = self.snap_image
        else:
            self.logger.info('Averaging {} frames for Snap'.format(N))
            self._pipeline.snap_list = []
            self._pipeline.collect_N_frames_in_snap_list = N
            self.start_free_run()
            while self._pipeline.collect_N_frames_in_snap_list:
                QTest.qWait(1)
            self.stop_free_run()
            self.snap_image = np.median(np.array(self._pipeline.snap_list[:N]), axis=0).astype(np.int16)
            self.temp_image = self.snap_image
            self.clear_statusbar()
        meta = {'exposure_time': self.config['camera']['exposure_time'],
                'averaged_over_N_frames': N}
        if self.save_image_object is not None:
            self.snap_number = self.save_image_object.save_single_snap(self.snap_image, meta_data=meta)
            self.logger.debug('restored ')

        # prev_img_save_callback = self._pipeline.save_img_func
        # prev_img_save_state = self._pipeline.save_img
        # # was_streaming = self.camera.is_streaming()
        # # if was_streaming:
        # #     self.stop_free_run()
        # class callback:
        #     def __init__(self):
        #         self.snap_list = []
        #         self.snap_count = 0
        #     def __call__(self, frame):
        #         self.snap_list.append(frame)
        #         self.snap_count += 1
        # #
        # # def callback(frame):
        # #     nonlocal snap_list, snap_count
        # #     snap_list.append(frame)
        # #     snap_count += 1
        # func = callback()
        # self._pipeline.set_save_img_func(func)
        # self.start_free_run()
        # while func.snap_count < N:
        #     QTest.qWait(1)
        # self.stop_free_run()
        # self._pipeline.unset_save_img_func()
        # # self.snap_image = np.round(np.mean(np.array(snap_list[:N]), axis=0)).astype(np.int16)
        # self.snap_image = np.median(np.array(func.snap_list[:N]), axis=0).astype(np.int16)
        # self.temp_image = self.snap_image
        # self._show_snap = True
        # if self.save_image_object is not None:
        #     self.save_image_object.save_single_snap(self.snap_image)
        #     self.logger.debug('restored ')
        # if prev_img_save_callback:
        #     self._pipeline.set_save_img_func(prev_img_save_callback)
        # self._pipeline.save_img = prev_img_save_state

        # if was_streaming:
        #     self.start_free_run()
        # show_avg_snap_ms = self.config['camera']['show_avg_snap_ms']
        # if was_streaming and show_avg_snap_ms > 0:
        #     QTest.qWait(show_avg_snap_ms)
        self._show_snap = False
        self.clear_statusbar()


    # def snap(self):
    #     """ Snap frames and average. Number of frames is defined in config.
    #     """
    #     # if not self.camera.is_streaming():
    #     #     img = np.zeros(self.camera.get_size(), dtype=np.uint16, order='C')
    #     #     self.camera.snap_into(img)
    #     #     self.snap_image = img.astype(np.int16)
    #     #     self.temp_image = self.snap_image
    #     #     if self.save_image_object is not None:
    #     #         self.save_image_object.save_single_snap(self.snap_image)
    #     N = self.config['camera']['snap_avg_N_frames']
    #     snap_list = []
    #     snap_count = 0
    #     if self.camera.is_streaming():  # while already acquiring
    #         while snap_count < N:
    #             self.snap_image = None
    #             while self.snap_image is None:  # wait until snap_imge
    #                 self.snap_image = self.temp_image
    #             snap_list.append(self.snap_image)
    #             snap_count += 1
    #     else:  # when not yet acquiring
    #         def callback(frame):
    #             nonlocal snap_list, snap_count
    #             # self.temp_image = frame
    #             # print('self.temp_image is updated', snap_count)
    #             snap_list.append(frame)
    #             snap_count += 1
    #         prev_img_save_callback = self._pipeline.save_img_func
    #         prev_img_save_state = self._pipeline.save_img
    #         self._pipeline.set_save_img_func(callback)
    #         self.start_free_run()
    #         while snap_count < N:
    #             QTest.qWait(2)
    #         self.stop_free_run()
    #         self._pipeline.unset_save_img_func()
    #         if prev_img_save_state:
    #             self._pipeline.set_save_img_func(prev_img_save_callback)
    #
    #         # x, y = self.camera.get_size()
    #         # bytes_per_frame = x*y*2
    #         # bytes_to_buffer = 1024*1024*128
    #         #
    #         # def callback(frame):
    #         #     nonlocal snap_list, snap_count
    #         #     self.temp_image = frame
    #         #     # print('self.temp_image is updated', snap_count)
    #         #     snap_list.append(frame)
    #         #     snap_count += 1
    #         #     # QTest.qWait(10)
    #         # self.camera.start_stream(int(bytes_to_buffer/bytes_per_frame), callback)
    #         # while snap_count < N:
    #         #     pass
    #         # self.camera.stop_stream()
    #     tmp = np.array(snap_list[:N])
    #     self.snap_image = np.round(np.mean(np.array(snap_list), axis=0)).astype(np.int16)
    #     t0 = time.time()
    #     while time.time() < t0 + 0.5:
    #         self.temp_image = self.snap_image


    def save_image(self):
        """ Saves the last acquired image. The file to which it is going to be saved is defined in the config.
        """
        if self.snap_image is None:
            self.logger.warning('Take a snapshot first')
        else:
            self.logger.info('Saving last acquired image')
            if not hasattr(self, 'hdf5_snaps'):
                self.hdf5_snaps = FileWrangler(os.path.join(self.save_path, self.config['saving']['filename_photo'])+'_'+self.hdf5.number)
            # Data will be appended to existing file

            now = str(datetime.now())
            device_grp = self.hdf5_snaps.file.require_group('data')
            aquisition_nr = len(device_grp.keys())

            device_grp.create_dataset('image_{}'.format(aquisition_nr+1), data=self.snap_image, meta_data={'example': 'snap meta'})
            # device_grp.create_dataset('metadata', data=yaml.dump(self.config))
            # device_grp.flush()
            self.hdf5_snaps.file.flush()
            # self.logger.debug('Saved image to {}'.format(os.path.join(file_dir, file_name)))
            self.snap_image = None


    #@make_async_thread
    # @check_not_acquiring
    # @check_camera
    def start_free_run(self):
        """ Starts continuous acquisition from the camera, but it is not being saved. This method is the workhorse
        of the program. While this method runs on its own thread, it will broadcast the images to be consumed by other
        methods. In this way it is possible to continuously save to hard drive, track particles, etc.
        """
        # return self.start_capture()
        x, y = self.camera.get_size()
        bytes_per_frame = x*y*2
        bytes_to_buffer = 1024*1024*128
        self.camera.start_stream(int(bytes_to_buffer/bytes_per_frame), self._pipeline)


    # def start_capture(self):
    # #   self.camera.stream_into(self.temp_image)
    #     aqcuisition = self.hdf5.start_new_aquisition()
    #     # self.daq_controller.set_processing_function(SaveDaqToHDF5(aqcuisition, self.daq_controller))
    #     self.save_trigger_object = SaveTriggerToHDF5(aqcuisition, self.daq_controller)
    #     self.daq_controller.set_trigger_processing_function(self.save_trigger_object)
    #
    #     # def temp(img_data):
    #     #     return SaveImageToHDF5(aqcuisition, img_data, self.config['camera']['save_every_Nth_frame'])
    #     #
    #     # self._pipeline.set_save_img_func(temp)
    #
    #     # Equivalent of the code above, but using a lambda-function:
    #     self._pipeline.set_save_img_func(lambda img: SaveImageToHDF5(aqcuisition, img, self.config['camera']['save_every_Nth_frame']))
    #     print('aaaaaaaaaaaaaaaaaa')
        # self.tracking = True
        # self.tracking = False
        # def update_trck(df):
        #     self.tracked_locations = df
        #     return df

        # pipeline = DataPipeline([SaveImageToHDF5(aqcuisition, self.camera, 10),update_img, ContinousTracker2(self.tracked_locations, rad=50), SaveTracksToHDF5(aqcuisition)])
        # x, y = self.camera.get_size()
        # bytes_per_frame = x*y*2
        # bytes_to_buffer = 1024*1024*128
    #     self.camera.start_stream(int(bytes_to_buffer/bytes_per_frame), pipeline)

    # @property
    # def temp_locations(self):
    #     return self.localize_particles_image(self.temp_image)

    def stop_free_run(self):
        # I THINK WE NEED TO SPLIT IT IN STOP_CAPTURE AND STOP_FREE_RUN
        """ Stops the free run by setting the ``_stop_event``. It is basically a convenience method to avoid
        having users dealing with somewhat lower level threading options.
        """
        self.camera.stop_stream()
        self.daq_controller.set_trigger_processing_function(None)
        self.daq_controller.set_processing_function(None)
        self.logger.debug("stream stopped in python!")

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
        # print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        # aqcuisition = self.hdf5.start_new_aquisition()
        # self._pipeline.set_save_img_func(
        #     lambda img: SaveImageToHDF5(aqcuisition, img, self.config['camera']['save_every_Nth_frame']))

        # print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')

        # Example of dumping the entire config as meta_data using yaml.
        # Note that after reading the hdf5 file (as f, this can be retrieved with:
        # d = yaml.safe_load(f['data']['Acquisition_0'].attrs['config'])

        aqcuisition = self.hdf5.start_new_aquisition(meta_data={'config':yaml.safe_dump(self.config)})
        self.aqcuisition = aqcuisition
        self.save_trigger_object = SaveTriggerToHDF5(aqcuisition, self.daq_controller, meta_data_trigger={'example':'trigger meta'}, meta_data_daq={'example':'daq meta'})
        self.daq_controller.set_trigger_processing_function(self.save_trigger_object)

        self.save_image_object = SaveImageToHDF5(aqcuisition, self.camera, 10, meta_data={'example':'image meta'})  # adding meta is optional
        self._pipeline.set_save_img_func(self.save_image_object) # TEMPRARILY DISABLED FOR DEBUGGING    TEMPRARILY DISABLED FOR DEBUGGING    TEMPRARILY DISABLED FOR DEBUGGING   TEMPRARILY DISABLED FOR DEBUGGING    TEMPRARILY DISABLED FOR DEBUGGING     TEMPRARILY DISABLED FOR DEBUGGING   TEMPRARILY DISABLED FOR DEBUGGING

        self.save_tracks_object = SaveTracksToHDF5(aqcuisition, meta_data={'example': 'track meta'})
        self._pipeline.add_process_img_func([ContinousTracker2(self.tracked_locations, self.config['analysis']['box_half_size']), self.save_tracks_object], 'track')
        # self._pipeline.add_process_img_func(SaveTracksToHDF5(aqcuisition), 'save_track')

        # self.save_trigger_object = SaveTriggerToHDF5(aqcuisition, self.daq_controller)
        # self.daq_controller.set_trigger_processing_function(self.save_trigger_object)

        # def temp(img_data):
        #     return SaveImageToHDF5(aqcuisition, img_data, self.config['camera']['save_every_Nth_frame'])
        #
        # self._pipeline.set_save_img_func(temp)

        # Equivalent of the code above, but using a lambda-function:


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
        self.logger.info('Stop saving stream')
        if hasattr(self.save_trigger_object, 'add_finished_timestamp'):
            self.save_trigger_object.add_finished_timestamp()
        self.save_tracks_object.add_finished_timestamp() #Note: trigger and DAQ finish process earlier than save_tracks by a couple of milliseconds
        self.save_image_object = None
        self.save_tracks_object = None

        self.daq_controller.set_trigger_processing_function(None)
        self._pipeline.unset_save_img_func()
        self._pipeline.clear_process_img_func_list()



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
        self.daq_controller.stop_all()
        self.hdf5.close()
        try:
            self.hdf5_snaps.close()
        except:
            pass
        super().finalize()

    def sysexcept(self, exc_type, exc_value, exc_traceback):
        self.logger.exception('Got an unhandled exception: {}'.format(exc_type))
        self.logger.exception('Traceback: {}'.format(exc_traceback))
        self.logger.exception('Value: {}'.format(exc_value))
        self.__exit__()
        sys.exit()

# OLD CODE   OLD CODE   OLD CODE   OLD CODE   OLD CODE   OLD CODE   OLD CODE   OLD CODE   OLD CODE   OLD CODE   OLD CODE
# CLASSES THAT DON'T APPEAR TO BE USED ANYMORE:

# class DataPipeline:
#     def __init__(self, callables_list = []) -> None:
#         self.callables_list = callables_list
#
#     def append_node(self, callable):
#         self.callables_list.append(callable)
#
#     def apply(self, data):
#         for c in self.callables_list:
#             # print("applying {} to {}".format(c, data))
#             data = c(data)
#             if data is None:
#                 return None
#         return data
#
#     def __call__(self, data):
#         self.apply(data)
#
#
# class ImageBuffer:
#     def __init__(self, buffer = None) -> None:
#         self.buffer = buffer
#     def __call__(self, image):
#         if self.buffer is None:
#             # print("setting buffer as it was empty")
#             self.buffer = np.copy(image)
#         else:
#             np.copyto(self.buffer, image, casting='no')
#         return image
#
# class Track:
#     def __init__(self, diameter = 11) -> None:
#         self.diameter = diameter
#     def __call__(self, image):
#         return tp.locate(image, self.diameter)
#
# class Batch:
#     def __init__(self, number) -> None:
#         self.number = number
#         self.buffer = None
#         self.index = 0
#     def __call__(self, data):
#         if self.buffer is None:
#             self.buffer = np.zeros((self.number,)+data.shape, data.dtype)
#         self.buffer[self.index,:] = data
#         self.index += 1
