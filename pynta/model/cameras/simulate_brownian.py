# -*- coding: utf-8 -*-
"""
    simulate_brownian.py
    ==================================
    The SimulatedBrownian class generates synthetic images corresponding to particles performing a thermal Brownian
    motion to be view, and eventually analyzed, by the rest of the pynta program.

    .. TODO:: Images could be generated a-priori and stored in memory. This would make it possible to generate higher
    framerates and specific sleep times between them.

    .. TODO:: A lot of parameters are stored as attributes of the class, but they are also used as arguments of methods.
    Either replace methods by functions are use the attributes instead of the arguments.

    :copyright:  Sanli Faez <s.faez@uu.com>
    :license: GPLv3, see LICENSE for more details
"""
import numpy as np


class SimBrownian:
    """
    :param loca: N x d array of coordinates for N particles in d dimensions, dimension can be intensity or point spread width
    :return: generated an image with specified noise and particles displaced accordingly
    """
    def __init__(self, size = (500, 100)):
        # camera and monitor parameters
        self.xsize, self.ysize = size
        # simulation parameters
        self.difcon = 2  # Desired diffusion constant in pixel squared per second
        self.numpar = 50  # Desired number of diffusing particles
        self.signal = 30  # brightness for each particle
        self.noise = 0  # background noise
        self.psize = 8  # half-spread of each particle in the image, currently must be integer
        x = np.arange(size[0])
        y = np.arange(size[1])
        X, Y = np.meshgrid(y, x)
        self.simbg = 0 #5+np.sin((X+Y)/self.psize) * 0
        self.initLocations()

    def initLocations(self):
        # initializes the random location of numpar particles in the frame. one can add more paramaters like intensity
        # and PSF distribution if necessary
        parx = np.random.uniform(0, self.xsize, size=(self.numpar, 1))
        pary = np.random.uniform(0, self.ysize, size=(self.numpar, 1))
        pari = np.random.uniform(1, self.numpar, size=(self.numpar, 1)) * self.signal
        self.loca = np.concatenate((parx, pary, pari), axis=1)
        self.loca = self.nextRandomStep()
        return self.loca

    def resizeView(self, size):
        """SimulateBrownian.resizeView() adjusts the coordinates of the moving particles such that they
        fit into the desired framesize of the simulated dummycamera"""
        x = np.arange(size[0])
        y = np.arange(size[1])
        X, Y = np.meshgrid(y, x)
        self.simbg = 0#  5+np.sin((X+Y)/self.psize)
        self.xsize, self.ysize = size
        self.loca = self.initLocations()
        return

    def nextRandomStep(self):
        numpar = self.numpar
        margin = 2*self.psize #margines for keeping whole particle spread inside the frame
        dr = np.random.normal(loc=0.0, scale=np.sqrt(self.difcon), size=(numpar, 2))
        locations = self.loca[:,0:2] + dr
        for n in range(0, numpar):
            locations[n, 0] = np.mod(locations[n, 0]-margin, self.xsize-2*margin)+margin
            locations[n, 1] = np.mod(locations[n, 1]-margin, self.ysize-2*margin)+margin

        self.loca[:,0:2] = locations

        return self.loca

    def genImage(self):
        """
        :return: generated image with specified noise and particles position in self.loca
        """

        simimage = np.random.uniform(1, self.noise, size=(self.xsize, self.ysize))# + self.simbg
        psize = self.psize
        normpar = np.zeros((2*psize, 2*psize))
        for x in range(psize):
            for y in range (psize):
                r = 2*(x**2+6*y**2)/psize**2
                normpar[psize-x, psize-y] = normpar[psize-x, psize+y] = normpar[psize+x, psize-y] = normpar[psize+x, psize+y] = np.exp(-r)
        for n in range(0, self.numpar):
            x = np.int(self.loca[n,0])
            y = np.int(self.loca[n,1])
            simimage[x-psize:x+psize, y-psize:y+psize] = simimage[x-psize:x+psize, y-psize:y+psize] + normpar * self.loca[n,2]
        return simimage


