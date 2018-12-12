# -*- coding: utf-8 -*-

from setuptools import setup

with open('pynta/__init__.py', 'r') as f:
    version_line = f.readline()

version = version_line.split('=')[1].strip()

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='pynta',
    version=version,
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
                      'pyzmq', 'numba'],
    long_description=long_description,
    long_description_content_type="text/markdown",
)

