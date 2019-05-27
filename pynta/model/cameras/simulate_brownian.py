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
    :param tuple camera_size: number of pixels in the x and y direction
    :return: generated an image with specified noise and particles displaced accordingly
    """
    num_particles = 50
    dif_coef = 1  # um^2/s
    magnification = 30  # Magnification of the microscope
    pixel_size = 5  # um
    NA = 1  # Numerical aperture of the objective, used to estimate PSF
    wavelength = .500  # um, used to estimate PSF
    signal = 30  # Peak intensity for a particle
    noise = 0  # Background noise
    time_step = 0.01  # s, Time step in the simulation. Should be set to the acquisition rate if used for a camera
    kernel_size = 11  # Number of pixels used to calculate the PSF of the particle
    def __init__(self, camera_size=(500, 500)):
        # camera and monitor parameters
        self.camera_size = np.array(camera_size)
        self.localization = np.zeros(shape=(self.num_particles, 2))
        self.real_space_size = self.camera_size*self.pixel_size/self.magnification
        self.real_space_margin = self.kernel_size*self.pixel_size/self.magnification
        self.localization = np.random.uniform([0, 0], self.real_space_size, size=(self.num_particles, 2))
        self.next_random_step()
        self.psf_width = self.magnification * self.wavelength/(2*self.NA)/self.pixel_size  # In pixels

    def resize_view(self, camera_size):
        """SimulateBrownian.resizeView() adjusts the coordinates of the moving particles such that they
        fit into the desired framesize of the simulated dummycamera"""
        # self.camera_size = np.array(camera_size)
        pass

    def next_random_step(self):
        dr = np.sqrt(self.time_step)*np.random.normal(loc=0.0, scale=np.sqrt(self.dif_coef), size=(self.num_particles, 2))
        self.localization += dr
        rem_x = np.mod(self.localization[:,0]-self.real_space_margin, self.real_space_size[0]-2*self.real_space_margin)+self.real_space_margin
        rem_y = np.mod(self.localization[:,1]-self.real_space_margin, self.real_space_size[1]-2*self.real_space_margin)+self.real_space_margin
        self.localization[:,0] = rem_x
        self.localization[:,1] = rem_y

    def gen_image(self):
        """
        :return: generated image with specified noise and particles position
        """
        img = np.zeros(self.camera_size)
        x = np.arange(-self.kernel_size, self.kernel_size+1)
        y = np.arange(-self.kernel_size, self.kernel_size+1)
        xx, yy = np.meshgrid(x, y)
        positions = self.localization*self.magnification/self.pixel_size  # In units of pixels (with sub-px accuracy)
        for p in positions:
            p_x = p[0]-int(p[0])
            p_y = p[1]-int(p[1])
            pix_x = int(p[0])
            pix_y = int(p[1])
            s_img = 1 / (np.sqrt(2 * np.pi)*self.psf_width) * np.exp(-((xx - p_x) ** 2 + (yy - p_y) ** 2)/(2*self.psf_width**2))
            img[pix_x-self.kernel_size:pix_x+self.kernel_size+1, pix_y-self.kernel_size:pix_y+self.kernel_size+1] += s_img
        return img*self.signal


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    sb = SimBrownian()
    img = sb.gen_image()
    plt.imshow(img)
    plt.show()
    sb.next_random_step()
    img2= sb.gen_image()
    plt.imshow(img2)
    plt.show()