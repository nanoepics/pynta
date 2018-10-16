"""
    openCET.View.LocateParticle.py
    ==================================
    The LocateParticle class contains necessary methods for localizing centroid of a particle and following its track.
    the idea is to make the output suitable for analysis with TrackPy of similar open-source tracking packages

    .. lastedit:: 10/5/2017
    .. sectionauthor:: Sanli Faez <s.faez@uu.nl>
"""
import numpy as np
import copy
#from scipy.ndimage.measurements import center_of_mass as cenmass

class LocatingParticle:
    """
    initiate the localization requirements
    :param psize: expected particle size (e.g. point spread function)
    :param step: expected step size for searching for next location
    :param noiselvl: noise level below which all image data will be set to zero
    :param iniloc: starting position [row, column] of the track passed by the monitoring routine
    :param imgsize: [number of rows, number of columns] in the analyzed image array
    [not implemented] consistently return success/failure messages regarding locating the particle
    """
    def __init__(self, psize, step, noiselvl, imgsize, iniloc):
        self.noise = noiselvl
        self.psize = psize
        self.step = step
        self.locx = iniloc[0]
        self.locy = iniloc[1]
        self.imgwidth = imgsize[0]
        self.imgheight = imgsize[1]
        print(imgsize, iniloc)

    def findParticleSize(self, data, location):
        """Estimates size of the PSF of the particle at the specified :location: in the :image:"""
        x, y = [int(location[0]), int(location[1])]
        w = 40 # distance of the expected peak from the crosshair pointer
        imgpart = data[x - w:x + w + 1, y - w:y + w + 1]
        imgpart[imgpart<self.noise] = 0
        if np.amax(imgpart)>self.noise:
            cx, cy = self.centroid(imgpart)
            self.locx, self.locy = [x-w+cx, y-w+cy]
            self.psize = np.int(np.sqrt(np.sum(imgpart)/np.amax(imgpart))) # very rough estimate, Gaussian fit can be better
        else:
            self.psize = 0
        return self.psize

    def centroid(self, data):
        h, w = np.shape(data)
        x = np.arange(0, w)
        y = np.arange(0, h)

        X, Y = np.meshgrid(x, y)

        cy = np.sum(X * data) / np.sum(data)
        cx = np.sum(Y * data) / np.sum(data)

        return [cx, cy]

    def pointspread(self, data, cx, cy):
        h, w = np.shape(data)
        x = np.arange(w) - cy
        y = np.arange(h) - cx

        X, Y = np.meshgrid(x, y)
        mass = np.sum(data)
        sy = np.sqrt(np.sum(np.square(X) * data) / mass)
        sx = np.sqrt(np.sum(np.square(Y) * data) / mass)

        return [sx, sy]

    def Locate(self, data_o):
        """extracts the particle localization information close the lastly known location (self.loc) and updates it"""
        data = copy.copy(data_o)
        x, y = [int(self.locx), int(self.locy)]
        w = np.int((self.psize + self.step)*2)
        if (x in np.arange(self.imgwidth-2*w-1)+w) and (y in np.arange(self.imgheight-2*w-1)+w):
            imgpart = data[x - w:x + w + 1, y - w:y + w + 1]
            imgpart[imgpart<self.noise] = 0 #note that this changes the actual data
            # for future: there should be checked that noise level is not set too high or too low
            if np.amax(imgpart)>2*self.noise:
                cx, cy = self.centroid(imgpart)
                self.locx, self.locy = [x-w+cx, y-w+cy]
                mass = np.sum(imgpart)
                sx, sy = self.pointspread(imgpart, cx, cy)
                tracktag = np.array([[mass, self.locx, self.locy, sx, sy]])
            else:
                tracktag = np.zeros((1, 5))

        else:
            tracktag = np.zeros((1,5))
            self.locx, self.locy = [0,0]

        #np.set_printoptions(precision=3)
        #print(tracktag) #for debugging purposes
        return tracktag