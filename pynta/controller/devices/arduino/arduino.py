"""
    arduino.py
    ==========

    Base driver for communicating with Arduino devices. In principle, Arduino's can be programmed in very different
    ways, and therefore the flow of information may be very different. This driver is thought to interface with
    an Arduino which is in control of two DC motors and which is able to read values from some devices, such as a
    DHT22, and a DS18B20.
"""

import pyvisa
# TODO: Make more flexible which bacend will be used for PyVisa
rm = pyvisa.ResourceManager('@py')


class Arduino:
    def __init__(self, port=None):
        """

        :param port: Serial port where the Arduino is connected, can be none and in order to look for devices
        automatically
        """
        self.rsc = None
        self.port = port
        if port:
            if not port.startswith('ASRL'):
                port = 'ASRL' + port
            self.port = port
            self.rsc = rm.open_resource(self.port)

    def write(self, command):
        self.rsc.write(command)

    def close(self):
        self.rsc.close()

    @staticmethod
    def list_devices():
        return rm.list_resources()

if __name__ == '__main__':
    print(Arduino.list_devices())

    inst = Arduino('COM3')
    inst.close()
    inst.list_devices()