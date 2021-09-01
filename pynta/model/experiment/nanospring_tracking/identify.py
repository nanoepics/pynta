"""
    CETgraph.tracking.identify.py
    ==================================
    Routines that are necessary for locating particles inside a frame and tracking them in a series of frames or in a waterfall data array

    .. lastedit:: 9/7/2017
    .. sectionauthor:: Sanli Faez <s.faez@uu.nl>
"""
import numpy as np
from .lib import calc
#from scipy import signal
import matplotlib.pyplot as plt

class TracksZ:
    """
    The "TracksZ" module recovers the track coordinates of multiple particles in a waterfall image as they go through
    the 1D field of view. It assumes uni-directional drift towards z = +inf.
    Optionally, new particles that emerge from the inlet will be automatically identified

    parameters needed to initiate the localization requirements
    :param psize: expected particle size (e.g. point spread function)
    :param step: expected diffusion distance in pixels to search for location in the next frame
    :param drift: expected drift in pixels per frame
    :param snr: expected signal to noise ratio for the peakfinder routine
    :param noiselvl: noise level below which all image data will be set to zero
    :param locations: location of particles in the last processed frame

    [not implemented] consistently return success/failure messages regarding locating the particle
    """
    def __init__(self, psize=8, step=1, drift=1, snr=50, noiselvl=1):
        self.noise = noiselvl
        self.psize = psize
        self.snr = snr
        self.step = step
        self.fov = 0
        self.nframes = 0
        self.drift = int(drift)
        self.fnumber = 0 # parameter that holds the last frame analyzed

    def locateInitialPosition(self, data):
        """
         finds initial position peaks in the first few lines; iterates as long as some peaks are found
         :param:
         data: kymograph data array with shape = (fov, nframes)
         :returns:
         possible location of particles in the first non-empty frame defines as peak intensity higher than 2*snr*noicelvl/psize
        """
        psize = self.psize
        fov, nframes = np.shape(data)
        self.fov = fov
        self.nframes = nframes
        min_signal = self.noise  # any value below min_signal will be set to zero, might cause miscalculation of actual intensity
        min_peak = self.noise * self.snr / psize
        #widths = np.arange(psize - 4, psize + 6)  # peak-widths that are acceptable for peak finder
        peak_indices = []
        cur_t = 0
        while (len(peak_indices) == 0 and cur_t < nframes):  # scanning frame by frame until finds the first peak larger than min_peak
            cur_line = np.copy(data[:, cur_t])
            pp = np.argmax(cur_line)
            if cur_line[pp] > min_peak:
                peak_indices = np.array([pp])
                print('Particle found in frame %d at position' % (cur_t), pp)
            #peak_indices = signal.find_peaks_cwt(cur_line, widths, min_snr=self.snr) #check help of scipy.signal for documentation
            cur_t += 1
        cur_line[cur_line < 2*self.noise] = 0 # setting all pixels bellow 2-sigma of noise level to zero
        cur_t -= 1
        self.fnumber = cur_t
        if not peak_indices:
            print('No peaks found! Try different parameters.')
        else:
            lp = peak_indices[0]
            cur_line = self.setLocalMaxZero(cur_line, lp)

            while (np.max(cur_line)>min_peak): # looking if there are extra peaks in the last analyzed frame
                pp = np.argmax(cur_line)
                if abs(pp-lp) > 2*psize:  #to make sure the new peak is separated enough from the previous peak
                    peak_indices = np.concatenate((peak_indices, [pp]), axis=0)
                    print('Particle found in frame %d at position' % (cur_t), pp)
                lp = pp
                cur_line = self.setLocalMaxZero(cur_line, lp)

            print('Particle(s) found in frame %d at positions' %(cur_t), peak_indices)
        return peak_indices

    def setLocalMaxZero(self, data, loca):
        """
        this method substracts the intensity of the single peak at position loca
        :param data: single line of a kymograph, shape = (fov, 1)
        :param loca: position of the peak that has to be subtracted
        """
        psize = 2*self.psize
        fov = self.fov
        pp = loca
        line = data
        winpar = np.arange(-psize, psize)
        winleft = np.arange(0, psize)
        winright = np.arange(fov - psize, fov)
        if pp < psize:
            line[winleft] = 0
        elif pp > fov - psize:
            line[winright] = 0
        else:
            line[loca+winpar] = 0

        return line

    def followLocalMax(self, data, loca, inlet = 'none'):
        """
        :param data: kymograph data array with shape = (fov, nframes)
        :param loca: initial position of peaks in the first frame, if set to empty, method will try to find initial location
        :param inlet: condition of adding extra peak to follow, 'left': entry from z=0, 'right': entry from z=fov, 'none': none
        :return: array with all particle coordinates in the format [0-'tag', 1-'t', 2-'mass', 3-'z', 4-'width']
        not that time is explicitly mentioned for the __future__ cases that particle might be missing for a few frame
        """
        fov, nframes = np.shape(data)
        psize = self.psize
        step = self.step
        drift = self.drift
        min_peak = self.noise * self.snr / psize
        winsearch = np.arange(drift - psize - step, psize + drift + step)  #indices of the segment around each peak to search for max in the next frame
        winpar = np.arange(-psize, psize)
        winleft = np.arange(0, psize + drift + step)
        winright = np.arange(fov - psize - step + drift, fov)
        self.fov = fov
        self.nframes = nframes
        if not len(loca):
            print('Cannot follow tracks when initial locations are empty!')
            return []
        else:
            locations = np.copy(loca)
            numpar = len(locations)
            tags = np.arange(numpar) #initiating particle tags for tracking
            lastpar = numpar-1
        tracks = []
        """
        Next comes tracing the peaks, new entries are not considered
        The following simplification are made for the following code
        - the average displacement is more than drift+step per frame
        - when tracks overlap, the rest of the track is common for two particle
          until they exit the field of view
        - tracks that gets closer to the limits of the fov than the psize will be discontinued  

        To be considered in the future
        - colocalization for particles that come too close
        - discontinuation of tracks for particles that suddenly disappear

        """
        for t in range(nframes):
            cur_line = data[:, t]
            dropflag = 0
            for p in range(numpar):
                pp = locations[p]
                if pp + winsearch[0] < 0:
                    seg = cur_line[winleft]
                    ori = 0
                    pp = ori + np.argmax(seg)
                    if pp > psize:
                        seg = cur_line[pp + winpar]
                        ori = pp + winpar[0]
                    peak_attr = calc.centroid1D(seg, ori)
                    pp = int(peak_attr[1])
                    locations[p] = pp
                    if pp > psize or inlet == 'left' : # only registers the location if the particle is not too close to the outlet edge
                        new_row = np.concatenate(([tags[p], t], peak_attr))
                        if not len(tracks):
                            tracks = [new_row]
                        else:
                            tracks = np.concatenate((tracks, [new_row]), axis=0)
                    else:  # drops tracks that get too close to the fov limits
                        newlocations = np.delete(locations, p)
                        print('Track %d dropped' %(tags[p]))
                        newtags = np.delete(tags, p)
                        dropflag = 1

                elif pp + winsearch[-1] > fov-1:
                    seg = cur_line[winright]
                    ori = winright[0]
                    pp = ori + np.argmax(seg)
                    if pp < fov - psize:
                        seg = cur_line[pp + winpar]
                        ori = pp + winpar[0]
                    peak_attr = calc.centroid1D(seg, ori)
                    pp = int(peak_attr[1])
                    locations[p] = pp
                    if pp < fov - psize or inlet == 'right': # only registers the location if the particle is not too close to the outlet edge
                        new_row = np.concatenate(([tags[p], t], peak_attr))
                        if not len(tracks):
                            tracks = [new_row]
                        else:
                            tracks = np.concatenate((tracks, [new_row]), axis=0)
                    else:  # drops tracks that get too close to the fov limits
                        newlocations = np.delete(locations, p)
                        print('Track %d dropped' %(tags[p]))
                        newtags = np.delete(tags, p)
                        dropflag = 1

                else:
                    seg = cur_line[winsearch + pp]
                    pp = pp + winsearch[0] + np.argmax(seg)
                    if pp + winpar[0]<0:
                        seg = cur_line[winleft]
                        ori = 0
                    elif pp + winpar[-1] > fov-1:
                        seg = cur_line[winright]
                        ori = winright[0]
                    else:
                        seg = cur_line[pp+winpar]
                        ori = pp + winpar[0]
                    peak_attr = calc.centroid1D(seg, ori)
                    pp = int(peak_attr[1])
                    locations[p] = pp
                    if peak_attr[0] > min_peak : # only registers if the particle mass is more than acceptable signal level
                        new_row = np.concatenate(([tags[p], t], peak_attr))
                        if not len(tracks):
                            tracks = [new_row]
                        else:
                            tracks = np.concatenate((tracks, [new_row]), axis=0)

            # if any track is dropped, locations should be updated
            if dropflag:
                locations = np.copy(newlocations)
                tags = np.copy(newtags)
                dropflag = 0
            # check if there is a new distinguishable particle close to the inlet
            if inlet == 'left':
                if np.min(locations) > 2*psize:
                    seg = cur_line[winleft]
                    ori = 0
                    if np.max(seg) > min_peak:
                        peak_attr = calc.centroid1D(seg, ori)
                        pp = int(peak_attr[1])
                        print('Particle found in frame %d at position %d' % (t, pp))
                        locations = np.concatenate((locations, [pp]), axis=0)
                        lastpar += 1
                        tags = np.concatenate((tags, [lastpar]), axis=0)

            elif inlet == 'right':
                if np.max(locations) < fov - 2*psize:
                    seg = cur_line[winright]
                    ori = winright[0]
                    if np.max(seg) > min_peak:
                        peak_attr = calc.centroid1D(seg, ori)
                        pp = int(peak_attr[1])
                        print('Particle found in frame %d at position %d' % (t, pp))
                        locations = np.concatenate((locations, [pp]), axis=0)
                        lastpar += 1
                        tags = np.concatenate((tags, [lastpar]), axis=0)

            numpar = len(locations)

            if (np.mod(t, 50) == 49):  #sort of progress bar
                print(t+1, 'frames analyzed. Latest locaitons:', locations)

        return tracks
