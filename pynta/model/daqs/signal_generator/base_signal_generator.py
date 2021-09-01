# -*- coding: utf-8 -*-
"""
    Base Signal Generator Model
    =================
    

    :copyright:  Hayley Deckers <h.deckers@students.uu.nl>
    :license: GPLv3, see LICENSE for more details
"""

#from pynta.model.cameras.decorators import not_implemented
from typing import Optional
from pynta.util.log import get_logger
from enum import Enum
from abc import ABCMeta, abstractmethod
#from pynta import Q_


#logger = get_logger(__name__)

class Waveform(Enum):
    Square = 1,
    Triangle = 2,
    Sine = 3,
    Arbitrary = 4

class SupportedValues:
    def __init__(self, values= [], is_range = False) -> None:
        self.__values = values
        self.__is_range = is_range

    @classmethod
    def from_range(cls, min, max) -> 'SupportedValues':
        return cls([min,max], True)
    @classmethod
    def from_set(cls, values) -> 'SupportedValues':
        cls(values, False)
    
    @property
    def is_range(self):
        return self.__is_range
    
    def get_range(self) -> 'Optional[tuple[float,float]]':
        if self.is_range:
            return (self.__values[0], self.__values[1])
        else:
            return None

#todo: group up all the parameters in a single class. So that instead of implementing 6 functions for all the support/set, we only need to implement 2 (which take/return more arguments)
class BaseSignalGenerator(metaclass = ABCMeta):
    @abstractmethod
    def supported_waveforms(self) -> 'set[Waveform]':
        pass

    @abstractmethod
    def supported_frequencies(self) -> SupportedValues:
        pass

    @abstractmethod
    def supported_amplitudes(self) -> SupportedValues:
        pass

    @abstractmethod
    def supported_offsets(self) -> SupportedValues:
        pass
    
    @abstractmethod
    def set_square_wave(self, frequency, amplitude, offset, duty_cycle):
        #throw exception
        pass
    
    @abstractmethod
    def set_sine_wave(self, frequency, amplitude, offset):
        pass

    @abstractmethod
    def set_arbitrary_wave(self, frequency, data):
        pass

    # def supports_live_updates(self) -> bool:
    #     return False

    # @abstractmethod
    # def set_frequency(self, frequency : float):
    #     pass

    # @abstractmethod
    # def set_amplitude(self, frequency : float):
    #     pass

    # @abstractmethod
    # def set_offset(self, frequency : float):
    #     pass

    # @abstractmethod
    # def set_waveform(self, waveform : Waveform):
    #     pass
    
    # @abstractmethod
    # def set_duty_cycle(self, duty_cycle : float):
    #     pass
    
    def __str__(self):
        return f"Abstract Signal Generator"
