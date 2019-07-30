PyNTA Models
============

Models are the place to develop the logic of how the devices are used and how the experiment is performed. You will find models for cameras and daqs. Cameras are heavily used in PyNTA, while DAQs where inherited from a previous incarnation and were left here as a reference and to speed up future developments in which not only a camera has to be controlled.

The model for the experiment is the easiest place where the developer can have a sense of what is going on under-the-hood. You can check, for example, :mod:`~pynta.model.experiment.nanoparticle_tracking.np_tracking.NPTracking` in order to see the steps that make a tracking measurement. Remember that the program runs with different threads and processes in parallel, and therefore the behavior may not be trivial to understand.

.. automodule:: pynta.model
    :members:
    :undoc-members:
    :show-inheritance:


.. toctree::
   :maxdepth: 1
   :caption: Available Models

   cameras/index
   daqs/index
   experiments/index


