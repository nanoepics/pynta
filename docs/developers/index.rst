.. _for_developers:

Information for Developers
==========================

In these pages you will find the information needed for expanding the codebase of PyNTA. You can go through the
documentation of every module by following the links at the bottom of the page. However, there are some general guidelines regarding how to understand the code that can help you pin point the specific parts of the program that you would like to modify.

The design pattern chosen for the program is called MVC, that stands for Model-View-Controller. This pattern splits the different attributions of the code in order to make it more reusable. You can find a discussion about the MVC for lab applications on `this website <https://www.uetke.com/blog/general/the-mvc-pattern-for-lab-projects/>`_. The general principle is that by generating clear differences between parts of the program, you can obtain a highly sustainable program. Below you can see a description of what every module is and how you can help expanding it.

Every module will have its own particularities, which are explained briefly below. For more information, you should see the individual documentation and go through the code to understand better how the program's architecture was developed. It is important to note that PyNTA is a highly parallelized program. It relies on **zeromq** to pass messages between different processes. We have implemented a publisher/subscriber architecture that allows one central process to broadcast messages which can be captured by any listening procedure. This enables to spin on or off processes without altering the code. Moreover, it would make a clear path for remote control, data storage, etc.

The decentralized architecture of PyNTA makes it very flexible and powerful, but it also makes the code base much harder to understand for novice developers. Asynchronous programming is not a trivial task and can confuse people who are new to programming complex solutions (the code is no longer read from top to bottom). **Zeromq** was easy to implement, but may not be the best performing library for heavy numpy applications. Better approaches may be found in the future without compromising the existing code.

Below you will find an introduction to the code architecture. Read through to understand where to find answers and where is the proper place to implement updates and solutions.

Controller
----------
In our definition of the MVC pattern, :mod:`~pynta.controller` are the drivers of the devices. Controllers for cameras, for example, rely on library files (.dll files on Windows, .so in Linux) that can be more or less documented. For example :mod:`~pynta.controller.devices.hamamatsu` uses the *DCAM-API*, while :mod:`~pynta.controller.devices.photonicscience` uses *scmoscam.dll*. Controllers should follow the specifications of each device as closely as possible. For instance, the units each devices uses for setting exposure times or framerates, etc. Moreover, they shouldn't implement anything that the device is not capable of doing. A clear example would be to set a region of interest. Some cameras support it but some don't. You could be tempted to apply a ROI in the software directly, but you shouldn't do it in the Controller, there is a better place as we will see later.

Controllers are not always plain python files, sometimes are entire packages on themselves. For instance, the controller for Basler cameras (PyPylons) or National Instruments cards (pyDAQmx) are packages on their own. Sometimes the controllers where developed by other people, like the case of the Hamamatsu code, which was borrowed from Zhuang's lab. If you explore the controllers folder, you will notice that there are some available, like the :mod:`~pynta.controller.devices.keysight` ,that holds the drivers for an oscilloscope and function generator. Those controllers are remnants of a different incarnation of PyNTA, but that may still be valuable for the future.

Model
-----
In the MVC pattern that we have defined earlier, :mod:`~pynta.model` is the place to define all the logic on how to use the devices is located. The core principle of splitting Controllers and Models is to separate what the device can do by design and what the user imposes to the devices. For example, imagine a camera which can acquire frames one by one. The controller would provide a way to snap a single-frame. However, a user may want to acquire a movie by developing a for-loop that acquires a series of frames. The controller should reflect the capacities of the device, while the model will include all the user-imposed logic.

A clear advantage of having models is that in the case where controllers are not part of the package, for example if the driver is provided by the manufacturer itself, a model will make explicit how the driver is used. For example, NI-cards are very complex devices, and if one wants to monitor a signal, there are several required steps, which can be written down as a method of a class and re-used as much as wanted. Models can make use of explicit units (through Pint), for example.

Models are not limited to devices, but they also make explicit how an experiment is performed. In PyNTA, there are available at least two different experimental models, one for performing nanoparticle tracking analysis in 2D images (the classical NTA) and one to perform tracking analysis in hollow optical fibers, i.e., 1-D nanoparticle tracking. In these experiment models, you can find all the steps and how they relate to each other. For example, you can't subtract background if you haven't acquired the background first, etc.

Models for the Cameras
^^^^^^^^^^^^^^^^^^^^^^
Imagine you have a camera that doesn't support setting a region of interest (ROI), you can still crop the resulting images in the software, giving the same result as what a camera that does support ROI does. By having an intermediate layer between the controllers and the users, it is possible to detach the specific logic of an experiment and the specifications of the devices. Moreover, it makes very straightforward to add new devices to the experiment, exchanging cameras, etc.

Therefore in :mod:`~pynta.model.cameras` is where we will develop classes that have always the same methods and outputs defined, but that behave completely different when communicating with the devices. The starting point is the :mod:`skeleton <pynta.model.cameras.skeleton>`, where the ``cameraBase`` class is defined. In this class all the methods and variables needed by the rest of the program are defined. This strategy not only allows to keep track of the functions, it also enables the subclassing, which will be discussed later.

Having models also allow to quickly change from one camera to another. For example, if one desires to switch from a :mod:`Hamamatsu <pynta.model.cameras.hamamatsu>` to a :mod:`PSI <pynta.model.cameras.psi>`, the only needed thing to do is to replace::

    from pynta.model.cameras.hamamatsu import camera

With::

    from pynta.model.cameras.psi import camera

As you see, both modules ``Hamamatsu`` and ``PSI`` define a class called camera. And this classes will have the same methods defined, therefore whatever code relies on camera will be working just fine. One of the obvious advantages of having a Model is that we can define a :mod:`Dummy Camera <pynta.model.cameras.dummyCamera>` that allows to test the code without being connected to any real device.

If you go through the code, you'll notice that the classes defined in Models inherit ``cameraBase`` from the :mod:`~pynta.model.cameras.skeleton`. The quick advantage of this is that any function defined in the skeleton will be already available in the child objects. Therefore, if you want to add a new function, let's say ``set_gain``, you will have to start by adding that method to the ``skeleton``. This will make the function readily available to all the models, even if just as a mockup or to ``raise NotImplementedError``. Then we can overload the method by defining it again in the class we are working on. It may be that not all the cameras are able to set a gain, and we can just leave a function that ``return True``. If it is a functionality that you expect any camera to have, for example triggering an image acquisition, you can set the skeleton function to ``raise NotImplementedError``. This will give a very descriptive error of what went wrong if you haven't implemented the function in your model class.

.. todo:: It is also possible to define the methods as ``@abstractmethods`` which will automatically raise an exception. It may be worth exploring this possibility if there are several developers involved.

Model for the Experiment
^^^^^^^^^^^^^^^^^^^^^^^^
The way a user interacts with a camera is only part of the logic of an experiment. There are a lot of different steps and conditions that a person needs in order to obtain data. In the case of PyNTA, one of the requirements would be to analyse the images being acquired by a camera in real time and track the particles on them. Therefore, the best solution in order to develop clear code is to generate a new class for the experiment itself. You can see it in :mod:`~pynta.model.experiment` (the general, base one) or on :mod:`~pynta.model.experiment.nanoparticle_tracking`, a more elaborated one.

The idea behind the experiment model is that it makes it very clear what the logic of the experiment is. You need to load a camera, you need to acquire a movie, you need to analyse the frames, etc. It is very easy to add new steps, change the order in which different things happen, etc. Depending on the developer, starting with the experiment model may be the best place to implement changes, since it makes it very clear what is happening and what can be improved. A good idea would be to start developing your own experiment as a command-line based tool.

View
----
In the MVC patter, :mod:`~pynta.view` is, as the name suggests, where the GUI is defined. Since we defined all the logic of the experiment in a separate class, the View takes care of only triggering specific steps of the experiment and displaying the results. In principle, the only logic present in the view modules is only for aesthetic reasons. For instance, disable a specific button while a measurement is going on, etc. However, it should be the experiment model the one that avoids triggering two measurements if it is not possible, etc. That guarantees a lower-level safety.

:mod:`~pynta.view` is where the GUI lives. Within the module, you will also find :mod:`pynta.view.GUI`, in which the different widgets that make up the window are defined and another folder called designer, where the Qt Designer files are located. Adapting the looks of a program should start by looking into the ``.ui`` files, then checking the associated widgets in the ``GUI`` module, in order to connect the proper signals, etc. and finally modifying the main view class.


.. toctree::
   :maxdepth: 1
   :caption: PyNTA API

   pynta
