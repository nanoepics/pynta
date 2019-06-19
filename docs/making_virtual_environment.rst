..  _python_virtual_environment:

Setting up a Python Virtual Environment
=======================================

This guide is thought for users on Windows that want to use virtual environments on their machines.

1.
    Run::

        pip.exe install virtualenv

    At this point you have a working installation of virtual environment that will allow you to isolate your development from your computer, ensuring no mistakes on versions will happen.
    Let's create a new working environment called Testing

7.
    Run::

        virtualenv.exe Testing

    This command will  create a folder called Testing, in which all the packages you are going to install are going to
    be kept.

8.
    To activate the Virtual Environment, run::

        .\Testing\Scripts\activate

    (The ``.`` at the beginning is very important). If an error happens (most likely) follow the instructions below.
    Windows has a weird way of handling execution policies and we are going to change that.

    Open PowerShell with administrator rights (normally, just right click on it and select run as administrator)
    Run the following command::

        Set-ExecutionPolicy RemoteSigned

    This will allow to run local scripts.
    Go back to the PowerShell without administrative rights and run again the script activate.

9.
    When you are inside a virtual environment, you should see the name between ``()`` appearing at the beginning of the command line.

    Now you are working on a safe development environment. If you run::

        pip freeze

    You will see a list of all the packages currently installed in your environment. The list should be empty.

10.
    To deactivate the virtual environment just run::

        deactivate

11.
    If you run ``freeze`` again, you will see all the packages installed in the computer::

        pip freeze

