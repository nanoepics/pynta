from pynta.model.cameras.dcam import Camera
import matplotlib.pyplot as plt
import numpy as np
from pynta import Q_
import time 

last_micro = 0

class frame_handler:
    def __init__(self):
        self.last_micro = 0
        self.last_sec = 0
        self.fps = 0
    def __call__(self, data):            
        if len(data) > 0:
            sec = data[-1][0].timestamp.sec
            micro = data[-1][0].timestamp.microsec
            # print(self.last_sec, sec)
            if self.last_sec == sec:
                dt = micro-self.last_micro
                self.fps = 1.0/(dt*1e-6)
                # print(self.fps)
            self.last_micro = micro
            self.last_sec = sec
        

print("creating cam")
cam = Camera(0)
print("init")
cam.initialize()
# print("set trigger")
# cam.set_acquisition_mode(cam.MODE_SINGLE_SHOT)
# print("rriggering")
# cam.trigger_camera()
# print("reading")
# data = cam.read_camera()

cam.set_acquisition_mode(cam.MODE_CONTINUOUS)
# print("rriggering")
# cam.trigger_camera()
cam.set_binning_1x1()
# offset = (1024,1024)
size = (512,512)
max_offset = (2048-size[0], 2048-size[1])

cam.set_exposure(Q_('35us'))
measurement = frame_handler()
cam.set_ROI((0,0+size[0]),(0,0+size[1]))

for offset_x in range(0,max_offset[0],256):
    for offset_y in range(0,max_offset[1],256): 
        cam.set_offset(offset_x,offset_y)
        cam.start_free_run(measurement)
        time.sleep(0.5)
        cam.stop_free_running()
        print(offset_x, offset_y, measurement.fps, cam.get_ROI())

# print("reading")
# for i in range(0,10_000):
#     data = cam.read_camera()
# cam.stopAcq()
# print(np.mean(data[-1]))
# plt.imshow(data[-1])
# plt.show()
time.sleep(1)
# print(measurement.fps)
# cam.set_offset(300,300)
# time.sleep(1)
print(measurement.fps)
cam.stop_free_running()
