import nidaqmx as nidaq
from nidaqmx.constants import AcquisitionType
import numpy as np
class NiUsb6216:
    def __init__(self, out_channel = 'Dev1/ao0', in_channel = 'Dev1/ai0'):
        #self.out_channel = out_channel
        self.out_task = nidaq.Task()
        self.in_task = nidaq.Task()
        #zero on start and stop
        self.out_task.ao_channels.add_ao_voltage_chan(out_channel, min_val=-10, max_val=10)
        self.in_task.ai_channels.add_ai_voltage_chan(in_channel, min_val=-10, max_val=10)
        self.out_task.out_stream.output_buf_size = 2
        self.out_task.timing.cfg_samp_clk_timing(1e3, sample_mode=AcquisitionType.CONTINUOUS, samps_per_chan=2)
        self.in_task.timing.cfg_samp_clk_timing(1e3, sample_mode=AcquisitionType.CONTINUOUS, samps_per_chan=2)
        self.in_task.register_every_n_samples_acquired_into_buffer_event(2, None)
        self.out_task.write(np.zeros(2))
        self.out_task.start()
        self.in_task.start()
        #this function will be called everytime there's new data, with the data as argument, and the GUI can hook onto this to display the data.
        self.display_fnc = lambda x: None
        #this function will be called everytime there's new data, with the data as argument. This is intended for processing the data such as saving or analysis.
        #it's a seperate function to decouple the presence of a GUI from the experiment logic. In general the experiment file is in charge of doing the data logic and the GUI displays data and controls the settings. 
        # there's no direct coupling between the two, it goes trough the model. This maintains that seperation.
        self.processing_fnc = lambda x: None
        self.data_size = (0,)
        self.data_type = np.float32 #is this correct?
    
    def __del__(self):
        print("destructing nidaq")
        #device has memory, try and set the channel to 0 when we're done.
        self.out_task.stop()
        self.in_task.stop()
        self.in_task.register_every_n_samples_acquired_into_buffer_event(2, None)
        self.out_task.timing.cfg_samp_clk_timing(1e3, sample_mode=AcquisitionType.CONTINUOUS, samps_per_chan=2)
        self.out_task.write(np.zeros(2))
        self.out_task.close()
        self.in_task.close()
    def get_size(self):
        return self.data_size
           
    def start_sine_task(self, frequency, amplitude, offset, n_points = 250):
        data = amplitude*np.sin(np.linspace(0, 2 * np.pi, endpoint=False, num=n_points))+offset
        return self.start_arbitrary_task(data, frequency)

    
    def start_square_task(self, frequency, amplitude, offset, duty_cycle, n_points = 250):
        flip_point = int(0.01*duty_cycle*n_points)
        data = np.ones(n_points)
        #todo: this can be done faster i'm sure
        for i in range(0, flip_point):
            data[i] = -1
        #flip amplitude so it starts high
        data = data*(-1*amplitude)+offset
        return self.start_arbitrary_task(data, frequency)
        
    
    def start_arbitrary_task(self, data, repetition_frequency):
        self.out_task.stop()
        #withot the next line, we sometimes see the error
        #   nidaqmx.errors.DaqError: Non-buffered hardware-timed operations are not supported for this device and Channel Type.
        #   Set the Buffer Size to greater than 0, do not configure Sample Clock timing, or set Sample Timing Type to On Demand.
        # as we want hardware sampling, we can't use on demand and need to set a buffer. It's supposed to do this automatically though?
        self.out_task.out_stream.output_buf_size = data.size
        self.out_task.timing.cfg_samp_clk_timing(repetition_frequency*data.size, sample_mode=AcquisitionType.CONTINUOUS, samps_per_chan=data.size)
        self.out_task.write(data)
        self.out_task.start()
    
    def capture_once(self, frequency, points):
        self.in_task.stop()
        self.in_task.timing.cfg_samp_clk_timing(frequency, sample_mode=AcquisitionType.FINITE, samps_per_chan=points)
        return self.in_task.read(points)
    
    def set_display_function(self, fnc):
        self.display_fnc = fnc
        
    def set_processing_function(self, fnc):
        self.processing_fnc = fnc

    def capture_stream(self, frequency, points):
        
        def inner_callback(task_handle, every_n_samples_event_type,
            number_of_samples, callback_data):
            samples = self.in_task.read(number_of_samples_per_channel=points)
            self.display_fnc(samples)
            self.processing_fnc(samples)
            return 0
        self.in_task.stop()
        self.data_size = (points,)
        self.in_task.timing.cfg_samp_clk_timing(frequency, sample_mode=AcquisitionType.CONTINUOUS, samps_per_chan=points)
        self.in_task.register_every_n_samples_acquired_into_buffer_event(points, None)
        self.in_task.register_every_n_samples_acquired_into_buffer_event(points, inner_callback)
        self.in_task.start()
