# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('pynta/__init__.py', 'r') as f:
    version_line = f.readline()

version = version_line.split('=')[1].strip().replace("'", "")

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='PyNTA',
    version=version,
    description='Python Nanoparticle Tracking Analysis',
    packages=find_packages(),
    url='https://github.com/nanoepics/pynta',
    license='GPLv3',
    author='Aquiles Carattino',
    author_email='aquiles@uetke.com',
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
    ],
    include_package_data=True,
    # install_requires=['pyqt5==5.9.2', 'numpy', 'pyqtgraph==0.10.0', 'pint', 'h5py', 'trackpy', 'pandas', 'pyyaml',
    #                   'pyzmq', 'numba', 'nidaqmx', 'setuptools_rust'],
    # install_requires=['pyqt==5.9.2', 'numpy', 'pyqtgraph==0.10.0', 'pint', 'h5py', 'trackpy', 'pandas', 'pyyaml',
    #                   'pyzmq', 'numba', 'nidaqmx', 'setuptools_rust'],
    install_requires=['nidaqmx', 'setuptools_rust'],

    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "pynta=pynta.__main__:main"
        ]
    }
)

# experimental:
try:
    import os
    os.system('pip install -e rust_modules\pynta_driver_glue')
    import pynta_drivers
except:
    print('INSTALLING PYNTA_DRIVER_GLUE FAILED')
    print(r'Navigate to \rust_modules\pynta_driver_glue\ and run "pip install -e ."')

