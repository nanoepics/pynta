.. _installing:

Installing
==========

Pynta can be installed directly with pip. The first step is to create a virtual environment on your machine in order to
avoid clashes with the versions of the dependencies. Virtual Environments are must-have tool, regardless of what you are
doing. You can read a discussion about them directly on
`Python For The Lab <https://www.pythonforthelab.com/blog/virtual-environment-is-a-must-have-tool/>`_. You can also see
how to create a virtual environment :ref:`python_virtual_environment`.

To install PyNTA you can run the following command::

    pip install git+https://github.com/nanoepics/pynta

This will get you the latest stable version of Pynta. If you, however, would like to test new features, you can download
the development branch of the program::

    pip install git+https://github.com/nanoepics/pynta@develop

Especially if you want to try the development version, you should install it in a virtual environment. We can't guarantee
that the development will be future compatible, i.e. that the program stays compatible with itself over time. One of the
highest risks is that an upgrade on the development branch may brake your config files or customizations you have done.

Moreover there is the risk of requiring dependencies that are not fully supported or that are later dropped.

Dependencies
------------
By default, when you install PyNTA, the following dependencies will be installed on your computer:

* trackpy
* pyqt5<5.11
* numpy
* pyqtgraph
* pint
* h5py
* pandas
* pyyaml
* pyzmq
* numba

However, not all dependencies are mandatory for the program to work. For instance, if you are not interested in the GUI
but are planning to run the program from the command line, you are free to skip PyQt5, Pyqtgraph.

**Numba** is used because it accelerates the tracking of particles with **trackpy**. But if it is not available on the
computer, the program will run anyways.

Trackpy
~~~~~~~
Trackpy is instrumental for the program to work correctly. This package is able to detect particles on an image based on
few parameters but also to link the particles together, building up single-particle traces. PyNTA uses trackpy to perform
all the detection and analysis in real time.

One of the constrains of trackpy is that it depends heavily on Pandas, which is a great tool while working in combination
with Jupyter notebooks, but is not that great for user interfaces. Which require to transform from Pandas Data Frames to
numpy arrays all the time.

PyQt5 and Pyqtgraph
~~~~~~~~~~~~~~~~~~~
The user interface is built on PyQt5 in combination with PyQtGraph. PyQt5 versions newer than 5.11 fail at installing
through the setup process (but they do work if installed directly with pip). If this bug is resolved, the constrain on the
version of PyQt to use should be lifted. Moreover, it is desirable to switch to PySide2 as soon as the project is mature.

Operating System Support
------------------------
PyNTA was tested both on Linux and Windows machines. However, the main environment for PyNTA to run is Windows 10. There
are some very fundamental differences on how processes are started between Linux and Windows that have mutual drawbacks.
For example, on Windows processes are spawned, meaning that classes are re-imported and not instantiated. Therefore,
processes don't start with a shared state. This prevents, for example, to start a new process for a method of a class.

This forced the architecture of the program to rely heavily on functions and not methods, making the code slightly more
convoluted than what was desirable. The approach works on Linux also, but the performance may not be optimal.