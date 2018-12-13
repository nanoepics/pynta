# -*- coding: utf-8 -*-
"""
    NI model class
    ==============
    **National Instruments model for acquiring and generating signals.**

    .. warning:: This model relies on the PyDAQmx package.

    This class defines several methods that are useful when dealing with experiments. For example, when acquiring an
    analog signal, the method `analog_input_setup` takes within its arguments a list of `Devices` and it takes care of
    checking their limits, connection port, etc.

    If you are planning to add something to your experiment that the NI class does not support yet, the best is to look
    at the documentation **NI-DAQmx C Reference Help** (http://zone.ni.com/reference/en-XX/help/370471AA-01/). PyDAQmx
    wrapped all the C functions, removing the initial 'DAQmx' from the name, and the task handle is implicitly defined.

    The logic to add a new function here would be, for example: check if there is already something similar happening,
    for example if the same type of channel is already covered in the class and try to build from that example. If not, go
    to the documentation of NI and try to build a quick and simple python script that does what you are expecting. In this
    way you can be sure you understood what you are supposed to achieve. Then, write methods within this class that allow
    you to setup and trigger the new task. Sometimes the splitting between setting up and triggering is useful, since it
    allow you to trigger several times the same task without redefining it.

    Bear in mind that you will have access to specific information from outside the NI class. For example you can pass
    devices as arguments, and they will carry all the information you set up in the YAML file. If what you need is not
    yet covered, go back to the YAML and add it, then continue editing the NI class. Remember that adding is easy, removing
    or renaming implies that you have to check all the downstream code, and being YML the first step, it will imply reviewing
    everything.


    :copyright:  Aquiles Carattino <aquiles@aquicarattino.com>
    :license: GPLv3, see LICENSE for more details
"""
try:
    import PyDAQmx as nidaq
except ModuleNotFoundError:
    print('In order to work with this version of PyNTA you need to install PyDAQmx')
    raise

import numpy as np
from pynta.config import config
from pynta.model.daqs.skeleton import DaqBase
from pynta import Q_


class ni(DaqBase):
    def __init__(self, daq_num=1):
        """Class trap for condensing tasks that can be used for interacting with an optical trap.
        session -- class with important variables, including the adq card.
        """
        super().__init__(daq_num)
        self.daq_num = daq_num
        self.monitorNum = []
        self.tasks = []
        self.nidaq = nidaq

    def analog_input_setup(self, conditions):
        """
        Sets up a task for acquaring a number of analog channels.
        conditions -- dictionary with the needed conditions to set up an acquisition.

        """
        t = nidaq.Task()
        dev = 'Dev%s' % self.daq_num
        devices = conditions['devices']
        if not isinstance(devices, list):
            channel = ["Dev%s/ai%s" % (self.daq_num, devices.properties['port'])]
            limit_min = [devices.properties['limits']['min']]
            limit_max = [devices.properties['limits']['max']]
        else:
            channel = []
            limit_max = []
            limit_min = []
            for dev in conditions['devices']:
                channel.append("Dev%s/ai%s" % (self.daq_num, dev.properties['port']))
                limit_min.append(dev.properties['limits']['min'])
                limit_max.append(dev.properties['limits']['max'])

        channels = ', '.join(channel)
        channels.encode('utf-8')
        freq = int(1 / conditions['accuracy'].to('s').magnitude)
        # freq = freq.magnitude
        print('Samples per second: {} Hz'.format(freq))

        if conditions['trigger'] == 'external':
            trigger = "/Dev%s/%s" % (self.daq_num, conditions['trigger_source'])
        else:
            trigger = ""
        if 'trigger_edge' in conditions:
            if conditions['trigger_edge'] == 'rising':
                trigger_edge = nidaq.DAQmx_Val_Rising
            elif conditions['trigger_edge'] == 'falling':
                trigger_edge = nidaq.DAQmx_Val_Falling
            else:
                print('Unrecognised trigger edge. Falling to default')
                trigger_edge = config.ni_trigger_edge
        else:
            trigger_edge = config.ni_trigger_edge

        if 'measure_mode' in conditions:
            measure_mode = conditions['measure_mode']
        else:
            measure_mode = config.ni_measure_mode

        t.CreateAIVoltageChan(channels, None, measure_mode, min(limit_min),
                              max(limit_max), nidaq.DAQmx_Val_Volts, None)

        if conditions['points'] > 0:
            if 'sampling' in conditions:
                if conditions['sampling'] == 'finite':
                    cont_finite = nidaq.DAQmx_Val_FiniteSamps
                elif conditions['sampling'] == 'continuous':
                    cont_finite = nidaq.DAQmx_Val_ContSamps
                else:
                    raise Exception('Sampling mode not understood')
            else:
                cont_finite = nidaq.DAQmx_Val_FiniteSamps
            num_points = conditions['points']
        else:
            cont_finite = nidaq.DAQmx_Val_ContSamps
            num_points = config.ni_buffer

        t.CfgSampClkTiming(trigger, freq, trigger_edge, cont_finite, num_points)

        if 'start_mode' in conditions:
            if conditions['start_mode'] == 'digital':
                trigger = "/Dev%s/%s" % (self.daq_num, conditions['start_source'])
                edge = config.ni_start_edge
                if 'start_edge' in conditions:
                    if conditions['start_edge'] == 'rising':
                        edge = ni.DAQmx_Val_Rising
                    elif conditions['start_edge'] == 'falling':
                        edge = nidaq.DAQmx_Val_Falling
                    else:
                        raise Warning('Trigger edge for starting not recognized. Falling to default')
                        edge = config.ni_start_edge

                t.CfgDigEdgeStartTrig(trigger, edge)
            elif conditions['start_mode'] == 'analog':
                raise Warning('Starting with an analog trigger is not yet implemented')
            elif conditions['start_mode'] == 'software':
                print('Software starting')
            else:
                raise Warning('Only digital, analog and software start triggers are supported.')

        self.tasks.append(t)
        return len(self.tasks) - 1

    def trigger_analog(self, task=None):
        """
        :param task: Task number to be triggered.
        :return:
        """
        if task is None:
            t = self.tasks[-1]
        else:
            t = self.tasks[task]
        t.StartTask()  # Starts the measurement.

    def read_analog(self, task, conditions):
        """Gets the analog values acquired with the triggerAnalog function. If more than one channel is acquired, the number of points corresponds to
        the number of points PER channel, while the buffer has to take into account the total number of points.

        conditions -- dictionary with the number of points ot be read
        """
        if task is None:
            task = len(self.tasks) - 1

        t = self.tasks[task]
        read = nidaq.int32()
        points = int(conditions['points'])
        if points > 0:
            if 'buffer_length' in conditions:
                data = np.zeros((int(conditions['buffer_length']),), dtype=np.float64)
            else:
                data = np.zeros((points,), dtype=np.float64)
        else:
            data = np.zeros((config.ni_buffer,), dtype=np.float64)

        if 'timeout' in conditions:
            tout = conditions['timeout']
        else:
            tout = config.ni_read_timeout

        t.ReadAnalogF64(points, tout, nidaq.DAQmx_Val_GroupByChannel,
                        data, len(data), nidaq.byref(read), None)
        values = read.value
        return values, data

    def from_volt_to_units(self, value, dev):
        pass

    def digital_output(self, port, status):
        """ Sets the port of the digital_output to status (either True or False)
        """
        t = nidaq.Task()
        dev = 'Dev%s' % self.daq_num
        channel = "Dev%s/%s" % (self.daq_num, port)
        t.CreateDOChan(channel, None, nidaq.DAQmx_Val_ChanPerLine)

        if status:
            status = -1  # With this value, the digital output is set to High
        else:
            status = 0
        t.WriteDigitalScalarU32(nidaq.bool32(True), 0, status, None)

    def from_units_to_volts(self, value, dev):
        units = Q_(dev.properties['calibration']['units'])
        slope = dev.properties['calibration']['slope'] * units
        offset = dev.properties['calibration']['offset'] * units
        value = value.to(units)
        value = value.m
        slope = slope.m
        offset = offset.m
        return (value - offset) / slope

    def analog_output_dc(self, conditions):
        """ Sets the analog output of the NI card. For the time being is thought as a DC constant value.

        :param dict conditions: specifies DEV and Value
        :return:
        """
        dev = conditions['dev']
        port = "Dev%s/ao%s" % (self.daq_num, dev.properties['port'])
        units = Q_(dev.properties['calibration']['units'])
        min_value = Q_(dev.properties['limits']['min']).to(units)
        max_value = Q_(dev.properties['limits']['max']).to(units)
        # Convert values to volts:
        value = conditions['value'].to(units)
        V = self.from_units_to_volts(value, dev)
        min_V = self.from_units_to_volts(min_value, dev)
        max_V = self.from_units_to_volts(max_value, dev)
        t = nidaq.Task()
        t.CreateAOVoltageChan(port, None, min_V, max_V, nidaq.DAQmx_Val_Volts, None)
        t.WriteAnalogScalarF64(nidaq.bool32(True), 0, V, None)
        t.StopTask()
        t.ClearTask()

    def analog_output_samples(self, conditions):
        """ Prepares an anlog output from an array of values.
        :param conditions: dictionary of conditions.
        :return:
        """
        t = nidaq.Task()
        dev = conditions['dev'][0]
        port = dev.properties['port']

        min_val = self.from_units_to_volts(dev.properties['limits']['min'], dev)
        max_val = self.from_units_to_volts(dev.properties['limits']['max'], dev)

        t.CreateAOVoltageChan('Dev%s/ao%s' % (self.daq_num, port), None, min_val, max_val, nidaq.DAQmx_Val_Volts,
                              None, )

        freq = int(1 / conditions['accuracy'].to('s').magnitude)
        num_points = len(conditions['data'])

        t.CfgSampClkTiming('', freq, config.ni_trigger_edge, nidaq.DAQmx_Val_FiniteSamps, num_points)

        auto_trigger = nidaq.bool32(0)
        timeout = -1
        dataLayout = nidaq.DAQmx_Val_GroupByChannel
        read = nidaq.int32()

        t.WriteAnalogF64(num_points, auto_trigger, timeout, dataLayout, conditions['data'], read, None)

        self.tasks.append(t)
        return len(self.tasks) - 1

    def is_task_complete(self, task):
        t = self.tasks[task]
        d = nidaq.bool32()
        an = t.GetTaskComplete(d)
        return d.value

    def stop_task(self, task=-1):
        t = self.tasks[task]
        t.StopTask()

    def clear_task(self, task):
        t = self.tasks[task]
        t.ClearTask()

    def reset_device(self):
        nidaq.DAQmxResetDevice('Dev%s' % self.daq_num)


if __name__ == '__main__':
    import time

    a = ni(2)
    a.digital_output('PFI1', False)
    time.sleep(0.1)
    a.digital_output('PFI1', True)