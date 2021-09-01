from .base_signal_generator import BaseSignalGenerator, Waveform, SupportedValues


class DummySignalGenerator(BaseSignalGenerator):
    def __init__(self) -> None:
        super().__init__()

    def supported_waveforms(self) -> 'set[Waveform]':
        return {Waveform.Square, Waveform.Sine}

    def supported_frequencies(self) -> SupportedValues:
        return SupportedValues.from_range(1, 50)

    def supported_amplitudes(self) -> SupportedValues:
        return SupportedValues.from_range(0, 5)

    def supported_offsets(self) -> SupportedValues:
        return SupportedValues.from_range(-1, 1)

    def set_square_wave(self, frequency, amplitude, offset, duty_cycle):
        print('Setting a square wave with frequency {}, amplitude {}, offset {} and duty_cycle {}'.format(frequency, amplitude, offset, duty_cycle))
    
    def set_sine_wave(self, frequency, amplitude, offset):
        print('Setting a sine wave with frequency {}, amplitude {}, offset {}'.format(frequency, amplitude, offset))

    def set_arbitrary_wave(self, frequency, data):
        pass

    def supports_live_updates(self) -> bool:
        return True
