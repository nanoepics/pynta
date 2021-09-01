from .base_signal_generator import BaseSignalGenerator, Waveform, SupportedValues
import struct


class StmSignalGenerator(BaseSignalGenerator):
    def __init__(self) -> None:
        super().__init__()
        self.file_handle = open('/dev/ttyACM0', 'wb')

    def supported_waveforms(self) -> 'set[Waveform]':
        return {Waveform.Square}

    def supported_frequencies(self) -> SupportedValues:
        return SupportedValues.from_range(1, 50)

    def supported_amplitudes(self) -> SupportedValues:
        return SupportedValues.from_range(1.65, 1.65)

    def supported_offsets(self) -> SupportedValues:
        return SupportedValues.from_range(1.65, 1.65)

    def set_waveform(self, waveform: Waveform):
        print("setting waveform to ", waveform)

    def set_frequency(self, frequency):
        print("setting frequency to {}".format(frequency))
        period_ms = 1000.0/frequency
        byte = int(period_ms/4)
        print("writting ", byte)
        self.file_handle.write(struct.pack("=B", byte))
        self.file_handle.flush()

    def set_amplitude(self, amplitude: float):
        print("setting amplitude to ", amplitude)

    def set_offset(self, offset: float):
        print("setting offset to ", offset)

    def set_duty_cycle(self, duty_cycle: float):
        print("setting duty_cycle to ", duty_cycle)

    def supports_live_updates(self) -> bool:
        return True
