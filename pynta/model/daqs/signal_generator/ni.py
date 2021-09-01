from .base_signal_generator import BaseSignalGenerator, Waveform, SupportedValues

class Ni6216Generator(BaseSignalGenerator):
    def __init__(self, controller) -> None:
        super().__init__()
        self.controller = controller

    def supported_waveforms(self) -> 'set[Waveform]':
        return {Waveform.Square, Waveform.Sine}

    # actually more complex, dependent upon how many points you want to use in the waveform
    def supported_frequencies(self) -> SupportedValues:
        return SupportedValues.from_range(0.1, 100)

    # offsets+amplitudes have to be within +-10V.
    def supported_amplitudes(self) -> SupportedValues:
        return SupportedValues.from_range(-10, 10)

    def supported_offsets(self) -> SupportedValues:
        return SupportedValues.from_range(-10, 10)

    def set_square_wave(self, frequency, amplitude, offset, duty_cycle):
        self.controller.start_square_task(frequency, amplitude, offset, duty_cycle)
    
    def set_sine_wave(self, frequency, amplitude, offset):
        self.controller.start_sine_task(frequency, amplitude, offset)

    def set_arbitrary_wave(self, frequency, data):
        pass

    def supports_live_updates(self) -> bool:
        return False
