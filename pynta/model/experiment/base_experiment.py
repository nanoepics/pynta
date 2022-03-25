# -*- coding: utf-8 -*-
"""
    base_experiment.py
    ==================
    Base class for the experiments. ``BaseExperiment`` defines the common patterns that every experiment should have.
    Importantly, it starts an independent process called publisher, that will be responsible for broadcasting messages
    that are appended to a queue. The messages rely on the pyZMQ library and should be tested further in order to
    assess their limitations. The general pattern is that of the PUB/SUB, with one publisher and several subscribers.

    The messages should include a *topic* and data. For this, the elements in the queue should be dictionaries with two
    keywords: **data** and **topic**. ``data['data']`` will be serialized through the use of cPickle, and is handled
    automatically by pyZQM through the use of ``send_pyobj``. The subscribers should be aware of this and use either
    unpickle or ``recv_pyobj``.

    In order to stop the publisher process, the string ``'stop'`` should be placed in ``data['data']``. The message
    will be broadcast and can be used to stop other processes, such as subscribers.

    .. TODO:: Check whether the serialization of objects with cPickle may be a bottleneck for performance.


    :copyright:  Aquiles Carattino <aquiles@uetke.com>
    :license: GPLv3, see LICENSE for more details
"""
from multiprocessing import Process, Event
from datetime import datetime
import yaml, os, h5py
import importlib
import numpy as np
from pynta.util import get_logger
from pynta.model.experiment.publisher import Publisher
from pynta.model.experiment.subscriber import subscriber


class BaseExperiment:
    """ Base class to define experiments. Should keep track of the basic methods needed regardless of the experiment
    to be performed. For instance, a way to start and a way to finalize a measurement.
    """
    def __init__(self, filename=None):
        self.config = {}  # Dictionary storing the configuration of the experiment
        self.logger = get_logger(name=__name__)
        self._threads = []
        self.publisher = Publisher()
        self.publisher.start()

        self._connections = []
        self.subscriber_events = []
        if filename:
            self.load_configuration(filename)
        self.initialize_camera()

        self.measurement_methods = {'no measurments defined': self.no_measurments_defined}

    """which folder view to use for the GUI. Let's differen experiments use different files.
    """
    def no_measurments_defined(self):
        self.logger.warning('No measurement methods in your experiment class')

    def gui_file(self):
        return None

    def initialize_camera(self):
        print("init cam!!!")
        """ Initializes the camera to be used to acquire data. The information on the camera should be provided in the
        configuration file and loaded with :meth:`~self.load_configuration`. It will load the camera assuming
        it is located in nanoparticle_tracking/model/cameras/[model].

        .. TODO:: Define how to load models from outside of PyNTA. E.g. from a user-specified folder.
        """
        # try:
        #     self.logger.info('Importing camera model {}'.format(self.config['camera']['model']))
        #     self.logger.debug('pynta.model.cameras.' + self.config['camera']['model'])

        #     camera_model_to_import = 'pynta.model.cameras.' + self.config['camera']['model']
        #     cam_module = importlib.import_module(camera_model_to_import)
        # except ModuleNotFoundError:
        #     self.logger.error('The model {} for the camera was not found'.format(self.config['camera']['model']))
        #     raise
        # except:
        #     self.logger.exception('Unhandled exception')
        #     raise

        # cam_init_arguments = self.config['camera']['init']

        # if 'extra_args' in self.config['camera']:
        #     self.logger.info('Initializing camera with extra arguments')
        #     self.logger.debug('cam_module.camera({}, {})'.format(cam_init_arguments, self.config['camera']['extra_args']))
        #     self.camera = cam_module.Camera(cam_init_arguments, *self.config['Camera']['extra_args'])
        # else:
        #     self.logger.info('Initializing camera without extra arguments')
        #     self.logger.debug('cam_module.camera({})'.format(cam_init_arguments))
        #     self.camera = cam_module.Camera(cam_init_arguments)

        # self.camera.initialize()
        self.current_width, self.current_height = self.camera.get_size()
        self.logger.info('Camera sensor ROI: {}px X {}px'.format(self.current_width, self.current_height))
        self.max_width, self.max_height = self.camera.get_max_size()
        self.logger.info('Camera sensor size: {}px X {}px'.format(self.max_width, self.max_height))

    def stop_publisher(self):
        """ Puts the proper data to the queue in order to stop the running publisher process
        """
        self.logger.info('Stopping the publisher')
        self.publisher.stop()
        self.stop_subscribers()

    def stop_subscribers(self):
        """ Puts the proper data into every alive subscriber in order to stop it.
        """
        self.logger.info('Stopping the subscribers')
        for event in self.subscriber_events:
            event.set()

        for connection in self._connections:
            if connection['process'].is_alive():
                self.logger.info('Stopping {}'.format(connection['method']))
                connection['event'].set()

    def connect(self, method, topic, *args, **kwargs):
        """ Async method that connects the running publisher to the given method on a specific topic.

        :param method: method that will be connected on a given topic
        :param str topic: the topic that will be used by the subscriber to discriminate what information to collect.
        :param args: extra arguments will be passed to the subscriber, which in turn will pass them to the function
        :param kwargs: extra keyword arguments will be passed to the subscriber, which in turn will pass them to the function
        """
        event = Event()
        self.logger.debug('Arguments: {}'.format(args))
        arguments = [method, topic, event]
        for arg in args:
            arguments.append(arg)

        self.logger.info('Connecting {} on topic {}'.format(method.__name__, topic))
        self.logger.debug('Arguments: {}'.format(args))
        self.logger.debug('KWarguments: {}'.format(kwargs))
        self._connections.append({
            'method':method.__name__,
            'topic': topic,
            'process': Process(target=subscriber, args=arguments, kwargs=kwargs),
            'event': event,
        })
        self._connections[-1]['process'].start()

    def load_configuration(self, filename):
        """ Loads the configuration file in YAML format.

        :param str filename: full path to where the configuration file is located.
        :raises FileNotFoundError: if the file does not exist.
        """
        self.logger.info('Loading configuration file {}'.format(filename))
        try:
            with open(filename, 'r') as f:
                self.config = yaml.safe_load(f)
                self.logger.debug('Config loaded')
                self.logger.debug(self.config)
        except FileNotFoundError:
            self.logger.error('The specified file {} could not be found'.format(filename))
            raise
        except Exception as e:
            self.logger.exception('Unhandled exception')
            raise

    def clear_threads(self):
        """ Keep only the threads that are alive.
        """
        self._threads = [thread for thread in self._threads if thread[1].is_alive()]

    @property
    def num_threads(self):
        return len(self._threads)

    @property
    def connections(self):
        return [conn for conn in self._connections if conn['process'].is_alive()]

    @property
    def alive_threads(self):
        alive_threads = 0
        for thread in self._threads:
            if thread[1].is_alive():
                alive_threads += 1
        return alive_threads

    @property
    def list_alive_threads(self):
        alive_threads = []
        for thread in self._threads:
            if thread[1].is_alive():
                alive_threads.append(thread)
        return alive_threads

    def set_up(self):
        """ Needs to be overridden by child classes.
        """
        pass

    def finalize(self):
        """ Needs to be overridden by child classes.
        """
        self.publisher.stop()

    def update_config(self, **kwargs):
        self.logger.info('Updating config')
        self.logger.debug('Config params: {}'.format(kwargs))
        self.config.update(**kwargs)

    def __enter__(self):
        self.set_up()
        return self

    def __exit__(self, *args):
        self.logger.info("Exiting the experiment")
        self.finalize()

        self.logger.debug('Number of open connections: {}'.format(len(self.connections)))
        for event in self.subscriber_events:
            event.set()

        for conn in self.connections:
            self.logger.debug('Waiting for {} to finish'.format(conn['method']))
            conn['process'].join()

        self.logger.info('Finished the base experiment')

        self.publisher.stop()


class DataPipeline:
    """
    Updates temp_image in the parent class.
    A single "save_img_func" can be set or unset.
    Multiple "process_img_functions" can be added and removed. These are run sequentially,
    the next one takes the output of the previous one as input

    """
    def __init__(self, parent) -> None:
        self.parent = parent
        self.save_img = False
        self.clear_process_img_func_list()

    def set_save_img_func(self, func):
        self.save_img_func = func
        self.save_img = True

    def unset_save_img_func(self):
        self.save_img = False

    def clear_process_img_func_list(self):
        self.process_img_funcs = []
        self.process_img_funcs_names = []

    def add_process_img_func(self, funcs, name):
        self.process_img_funcs.append(funcs)
        self.process_img_funcs_names.append(name)

    def remove_process_img_func(self, name):
        try:
            i = self.process_img_funcs_names.index(name)
            self.process_img_funcs.pop(i)
            self.process_img_funcs_names.pop(i)
        except:
            pass

    def __call__(self, data):
        self.parent.temp_image = data
        if self.save_img:
            self.save_img_func(data)

        for funcs in self.process_img_funcs:
            if type(funcs) is list:
                new_data = data.copy()
                for func in funcs:
                    new_data = func(new_data)
            else:
                func(data)


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

class SaveTriggerToHDF5:
    def __init__(self, aqcuisition_grp, device, edge=1):
        #self.dataset_writer = dataset_writer
        self.counter = 0
        self.device_size = device.get_size()
        self.dataset_writer_daq = aqcuisition_grp.create_dataset("DAQ-input", shape=(0,)+self.device_size, dtype=device.data_type, maxshape=(None,)+self.device_size, chunks=(1,)+self.device_size, compression='gzip')
        # self.dataset_writer_trigger = aqcuisition_grp.create_dataset("trigger", shape=(0,)+device.get_size(), dtype=device.data_type, maxshape=(None,)+device.get_size(), chunks=(1,)+device.get_size(), compression='gzip')
        self.dataset_writer_trigger = aqcuisition_grp.create_dataset("trigger", shape=(0,), dtype=np.int64, maxshape=(None,), compression='gzip')
        # write out the signal generator settings.
        #self.dataset_writer.attrs["stride"] = stride
        t0 = str(datetime.utcnow())
        self.dataset_writer_daq.attrs["creation"]  = t0
        self.dataset_writer_trigger.attrs["creation"]  = t0
        self.dataset_writer_daq.attrs["frequency"]  = device._sample_freq
        self.dataset_writer_trigger.attrs["frequency"]  = device._sample_freq
        self.edge = edge
        self.daq_frame_count = 0
        self.previous_level = None
    def add_finished_timestamp(self):
        t_end = str(datetime.utcnow())
        self.dataset_writer_daq.attrs["finished"]  = t_end
        self.dataset_writer_trigger.attrs["finished"]  = t_end
    def __call__(self, data):
        dsize_daq = self.dataset_writer_daq.shape
        dsize_trigger = self.dataset_writer_trigger.shape
        self.dataset_writer_daq.resize((dsize_daq[0]+1,) + dsize_daq[1:])
        self.dataset_writer_daq[-1,:] = data[0]

        if self.previous_level is None:
            self.previous_level = data[1][0]  # If it is the first "window", make up "previous level" (the same as the first datapoint, so it won't register as a value change)
        # Note, the last value of the previous window is prepended in order to catch state changes that might occur right at the edge of a window
        trig = (np.array([self.previous_level] + data[1]) > 1.6).astype(int)

        # THIS LINE IS FOR TESTING WITHOUT ACTUAL TRIGGERS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # trig = (np.array([0,0,3,3,3,0,0,3,3,0,0]) > 1.6).astype(int)

        self.previous_level = data[1][-1]  # store the last value for the next iteration
        trig_indices = np.where(np.diff(trig) == self.edge)[0] + self.daq_frame_count * self.device_size[0]  # The +1 is removed because one value is prepended to the array
        self.daq_frame_count += 1
        if len(trig_indices):
            current_size = dsize_trigger[0]
            self.dataset_writer_trigger.resize((current_size + len(trig_indices),))
            self.dataset_writer_trigger[current_size:] = trig_indices


        # self.dataset_writer_trigger.resize((dsize_trigger[0]+1,) + dsize_trigger[1:])
        # self.dataset_writer_trigger[-1,:] = data[1]
        return data[0]

class FileWrangler:
    def __init__(self, filename, ext='.hdf5') -> None:
        if not filename.endswith(ext):
            filename += ext
        while os.path.exists(filename):
            base_name = filename[:-len(ext)].split('_')
            if base_name[-1].isnumeric():
                base_name[-1] = str(int(base_name[-1]) + 1)
            else:
                base_name += '1'
            filename = '_'.join(base_name) + ext
        self.filename = filename
        self.file = h5py.File(filename,'w',  libver='latest')
        self.file.attrs["creation"] = str(datetime.utcnow())


    def start_new_aquisition(self):
        #print("starting aq of {}".format(device))
        device_grp = self.file.require_group('data')
        aquisition_nr = len(device_grp.keys())
        grp = device_grp.create_group("Acquisition_{}".format(aquisition_nr))
        return grp
