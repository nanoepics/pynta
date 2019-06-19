.. _example-config:

The Config File
===============
To start the program, it is necessary to define a configuration file. You can :download:`get a config file here <media/example_config.yml>`. However, the best place to find the latest examples of config files is on the
`Github Repository <https://www.github.com/nanoepics/pynta>`_. The idea behind the config file is that it makes it
transparent both to the end user and to the developer the different settings available throughout the program.

The example config files only show the minimum possible contents. You are free to add as many entries as you would like.
However, they are not going to be displayed in the GUI, nor will be used automatically. They will, however, be stored as
metadata together with all the files. You could use the config file in order to annotate your experiments, for example.

The Format
----------
The config file is formatted as a YAML file. These files are very easy to transform into python dictionaries and are very
easy to type. So, for example, to change how the tracking algorithm works, one would change the following lines:

.. code-block:: yaml

    tracking:
      locate:
        diameter: 11  # Diameter of the particles (in pixels) to track, has to be an odd number
        invert: False
        minmass: 100

Note that for the file to make sense, it has to be indexed with 2 spaces. When reading it, it automatically converts some
data types. For example, diameter will be available as ``config['tracking']['locate']['diameter']`` and will be of type
integer. ``invert`` will be a boolean, etc. If the data type is not clear, the default is a string. So, for example:

.. code-block:: yaml

    camera:
      exposure_time: 30ms # Initial exposure time (in ms)

Will generate a ``config['camera']['exposure_time']`` of type string, that will need to be transformed to a quantity
later on. Note also that comments are ignored (after the ``#`` nothing is read).

Real Cameras
------------
Currently Pynta supports a handful of cameras. If you would like to load a hamamatsu camera, you should change the following line:

.. code-block:: yaml

    camera:
      model: dummy_camera

with the following:

.. code-block:: yaml
    :emphasize-lines: 2

    camera:
      model: hamamatsu

If you would like to understand how the loading of the camera works, in order to add your own, you can check :func:`~pynta.model.experiment.nano_cet.win_nanocet.NanoCET.initialize_camera`.

