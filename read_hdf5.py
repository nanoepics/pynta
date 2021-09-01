import h5py
import numpy as np
import matplotlib.pyplot as plt
with h5py.File("first_led_series.hdf5", 'r') as f:
    acq = f["data/Acquisition_2"]
    images = acq["Image"]
    signal = np.asarray(acq["DAQ-input"]).flatten()
    print(signal.shape)
    print(images.shape)
    intensities = np.mean(images, (1,2))
    print(intensities.shape)
    intensities -= np.min(intensities)
    intensities /= np.max(intensities)
    plt.plot(np.linspace(0,1, len(intensities)), intensities)
    plt.plot(np.linspace(0,1, len(signal)), signal/np.max(signal))
    plt.show()
