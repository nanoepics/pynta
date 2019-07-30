"""
    Devices
    =======
    Collection of drivers for different devices which are useful to perform measurements. Drivers may depend on
    external libraries. Thus, be aware that you may need to install some dependencies in order to make the
    controllers work correctly. A common example is the requirement of pyvisa to communicate with serial devices,
    or the DLL's from Hamamatsu in order to use their cameras.

    For several devices, drivers in Python are provided by the manufacturers and thus they won't be found in this
    module. A clear example is the Python wrapper of Pylon to work with Basler cameras, known as PyPylon. In that case,
    PyNTA only provides a model which relies on that package. For DAQ devices such as those from National Instruments,
    PyNTA depends on PyDAQmx, although NI has released its own wrapper,
    `NIDAQmx-Python <https://github.com/ni/nidaqmx-python>`_ which may be worth exploring.
"""

