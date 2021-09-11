import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import pynta_drivers

buffer = np.zeros((2048,2048), dtype=np.uint16)
cam = pynta_drivers.Camera("Dummy")
cam.stream_into(buffer)

fig = plt.figure()
im = plt.imshow(buffer, vmin=0, vmax=350)

def animate(i):
    im.set_data(buffer)
    return im

anim = animation.FuncAnimation(fig, animate,interval=4)
plt.show()