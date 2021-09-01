# PyNTA
## Particle tracking instrumentation and analysis in Python

![Screenshot of the PyNTA software](docs/media/screenshot_01.png?raw=true "PyNTA acquiring")

PyNTA aims at bridging the gap between data acquisition and analysis in nanoparticle tracking experiments. You can read more about the project at [https://python-nta.readthedocs.io](https://python-nta.readthedocs.io).

## Installation

### for developers
First create a virtual environment using 

    python3 -m venv env

and activate it with 

    source env/bin/activate

on Linux, or 

    .\env\Scripts\activate

on Windows.

Then install the required packages using 

    pip install -e .
    
the `-e` flag will install the program in edit mode. Now you can run pynta from the command line by typing `pynta` and any changes made in this repo will automatically be used.
## Starting PyNTA
In order to start the program, you need to run the following command: 

    pynta
    
It will automatically start the program with a default synthetic camera. If you would like to specify your own configuration file for PyNTA, you should run instead:

    pynta -c config.yml
    
where ``config.yml`` has to be replaced by the name of your file. You can explore the [examples folder](https://github.com/nanoepics/pynta/tree/master/examples) in the repository.

## First Steps with PyNTA
By default, PyNTA comes configures to use synthetic data. The images displayed are simulated random movements of particles. You can use that data to test the program regardless of whether you have a camera available or not. 

You can start by aquiring images and movies. Stream the data to the hard drive and do real time tracking and characterization based on the diffusion of the particles. You can find more information on the [online documentation](http://nanoepics.github.io/pynta).

## Supported cameras
We currently support the following cameras:
* **Hamamatsu Orca** (which interface through DCAM-API)
* **Photonic Science** 
* **Basler**

The code has been structured in such a way that adding support for other cameras is straightforward, and also the simulation of experiments is easy to implement. You can read the guide on how to contribute to the code. 

## Features
The key feature of PyNTA is the ability to acquire and analyse images in real time. By leveraging the capabilities of Trackpy, every frame is processed, detecting particles and linking their trajectories. This allows the user to see results about the distribution of particle sizes in close-to real time. 

PyNTA allows the user to stream data directly to the hard drive, both video data and particle location can be saved during the progress of the experiment, making it failsafe against failures. Metadata is included in every generated file, guaranteeing the reproducibility of the experiments. 

## Report Issues
To report a problem with PyNTA, or suggestions for improvement, etc. you can use the [Issue Tracking System](https://github.com/nanoepics/pynta/issues). You can also contact the authors of the program if you have specific needs or would like to collaborate either scientifically or with development of code.

## Wishlist
* Make PyNTA available for data analysis of data already collected
* Simplify the generation of the configuration file
* Encapsulate the experiment and isolate it from the GUI
* Improve response time for calculating size histograms
* Include extra parameters for the tracking, currently supported by trackpy but not implemented in the GUI
* Create an installer easy to distribute

## For Developers
You can find the source code of this project on [Github](https://github.com/nanoepics/pynta). You can check [the documentation](https://nanoepics.github.io/pynta) in order to understand the structure of the code and the main development guidelines. 

In summary, if you want to add or improve the code, the proper workflow is as follows: 

* Fork the repository into your own user space on Github.
* Start a new branch based on develop if you are adding new functionality or on master if you are solving an ASAP bug.
* Improve the code on that branch.
* Once you are done, update your branch with the latest code from develop:

    ```
    git checkout develop
    git pull upstream develop
    git rebase develop my_branch
    ```
    
    where `my_branch` is the name of the branch you have started. More info [here](https://git-scm.com/docs/git-rebase).
* This leaves your branch with a history appended to the end of the history of develop. Then, you can just merge the branch into develop with ``--squash``:
    ```
    git merge --squash my_branch
    git commit -m "description of your work"
    ```
    **Important**: When you do this, all the work that you have done on your branch will be condensed to a single commit into develop. Make sure you use a clear message. This makes tracking changes much easier, and the history of commits remains safe in your own repository.