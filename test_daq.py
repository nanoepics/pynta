from pynta.controller.devices.NIDAQ.ni_usb_6216 import NiUsb6216
from array import array
import time

file = open("out.bin", "wb")

def print_progress(data):
    print("writing...")
    array('d', data).tofile(file)
    return 0

def main():
    controller = NiUsb6216()
    controller.start_sine_task(5, 3.5, 0.0)
    data = controller.capture_once(2_000, 100)
    print(data)
    print("streaming...")
    controller.capture_stream(10_000, 500, print_progress)
    time.sleep(10)


print("python starts!")
main()
print("and now it exits...")
file.close()