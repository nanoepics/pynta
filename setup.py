# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='pynta',
    version='0.0',
    description='Python Nanoparticle Tracking Analysis',
    packages=['pynta',
              ],
    url='https://github.com/nanoepics/pynta',
    license='GPLv3',
    author='Aquiles Carattino',
    author_email='aquiles@aquicarattino.com',
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
    ],
    package_data={'pynta': ['View/GUI/Icons/*.*']},
    include_package_data=True,
    install_requires=['pyqt5<5.11', 'numpy', 'pyqtgraph', 'pint', 'h5py', 'trackpy', 'pandas', 'pyyaml',
                      'pyzmq', 'numba']
)
