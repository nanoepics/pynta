# pynta
##Particle tracking instrumentation and analysis in Python

![Alt text](doc/resources/screenshot.png?raw=true "Optional Title")

## Screenshot ##

![Screenshot of the PyNTA software](doc/media/screenshot_01.png?raw=true "PyNTA acquiring")

## Installation
Create a virtual environment in your own computer and run the following command to get the latest PyNTA version:

    pip install git+https://github.com/nanoepics/pynta

And if you want the development branch, you can run:

    pip install git+https://github.com/nanoepics/pynta@develop
    
Note that the development branch is for testing purposes only. Forward 
compatibility is not ensured and unexpected bugs may be encountered.

## For Developers
If you want to add or improve the code, the proper workflow is as follows: 

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