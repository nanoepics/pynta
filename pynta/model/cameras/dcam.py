import pynta.controller.devices.hamamatsu.dcam as dcam
from pynta.model.cameras.base_camera import BaseCamera
from pynta import Q_

import time
import numpy as np
import atexit
#NOTE(hayley): The documenataion says "The DCAM_IDPROP_SUBARRAYHPOS and DCAM_IDPROP_SUBARRAYVPOS properties can be changed during any state including BUSY status as they do not affect the data stream. The DCAM_IDPROP_SUBARRAYHSIZE and DCAM_IDPROP_SUBARRAYVSIZE properties can only the changed during UNSTABLE or STABLE state. These values are specified by sensor pixel unit therefore properties such as binning will not affect this value."
#              but this is a bold faced _LIE_ >:[ and triggers the BUSY error without updating the value.

#TODO(hayley): add checks for properties that can't be changed while capturing (BUSY state).

class Camera(BaseCamera):
    ActiveCameras = 0
    def __init__(self, camera_id):
        if Camera.ActiveCameras == 0:
            dcam.Dcamapi.init()
            Camera.ActiveCameras += 1
        camera = dcam.Dcam(camera_id)
        #TODO(hayley) handle with lasterr()
        assert camera.dev_open()
        Camera.ActiveCameras += 1
        #gracefully shutdown dcamapi when program is terminated.
        atexit.register(self.close)
        super().__init__(camera)

        self.running = False
        self.data_type = np.uint16
        self.n_buffers = 0
        self.seconds_to_buffer = 2.0
        self.set_prop(dcam.DCAM_IDPROP.SUBARRAYMODE, dcam.DCAMPROP.MODE.ON)
        self.last_frame = -1
        self.last_frame_idx = -1
           
    #TODO(hayley): these funcions come from the base model but feel out of place and don't match the naming scheme used
    def GetCCDWidth(self):
        return int(self.get_prop(dcam.DCAM_IDPROP.IMAGE_WIDTH))

    def GetCCDHeight(self):
        return int(self.get_prop(dcam.DCAM_IDPROP.IMAGE_HEIGHT))

    def get_max_size(self):
        return (self.max_width, self.max_height)

    def set_exposure(self, exposure):
        return super().set_exposure(exposure)
    
    def _allocate_buffers(self, n):
        if self.n_buffers != n:
            self.camera.buf_release()
            assert self.camera.buf_alloc(n)
            self.n_buffers = n

    def start_acquisition(self, mode = None):
        # print("start acq", self.camera.cap_status())
        self.running = True
        if mode is not None:
            self.set_acquisition_mode(mode)

        if self.mode == Camera.MODE_SINGLE_SHOT:
            self._allocate_buffers(1)
        elif self.mode == Camera.MODE_CONTINUOUS:
            # We allocate enough to buffer 2 seconds of data.
            n_buffers = int(self.seconds_to_buffer * self.get_prop(dcam.DCAM_IDPROP.INTERNALFRAMERATE))
            self._allocate_buffers(n_buffers)
            # print("alloc buff", self.camera.cap_status())
            self.last_frame = -1
            self.last_frame_idx = -1
            assert self.camera.cap_start()
            # print("cap started", self.camera.cap_status())
        else:
            #TODO(hayley): Hamamatsu model has reference to external but base does not.
            assert False

    def stop_acquisition(self):
        if self.mode == self.MODE_CONTINUOUS:
            self.camera.cap_stop()
        self.camera.buf_release()
        self.n_buffers = 0
        self.running = False
    
    def stopAcq(self):
        return self.stop_acquisition()

    def set_ROI(self, X, Y):
        # print("{} setting ROI to {}, {}".format(self.camera.cap_status(), X,Y))
        self.set_prop(dcam.DCAM_IDPROP.SUBARRAYHPOS, 0)
        self.set_prop(dcam.DCAM_IDPROP.SUBARRAYVPOS, 0)
        #needs multiple of 4?
        hsize = round(abs(X[0]-X[1])/4)*4
        hpos = round(X[0]/4)*4
        vsize = round(abs(Y[0]-Y[1])/4)*4
        vpos = round(Y[0]/4)*4
        #flipped x-y
        self.set_prop(dcam.DCAM_IDPROP.SUBARRAYVSIZE, hsize)
        self.set_prop(dcam.DCAM_IDPROP.SUBARRAYHSIZE, vsize)
        self.set_prop(dcam.DCAM_IDPROP.SUBARRAYVPOS, hpos)
        self.set_prop(dcam.DCAM_IDPROP.SUBARRAYHPOS, vpos)
        # print(self.get_size())
        return self.get_size()
    
    def set_offset(self, X, Y):
        # print("{} setting offset to {}, {}".format(self.camera.cap_status(), X,Y))
        # #needs multiple of 4?
        hpos = round(X/4)*4
        vpos = round(Y/4)*4
        #flipped x-y
        # self.set_prop(dcam.DCAM_IDPROP.SUBARRAYVSIZE, hsize)
        # self.set_prop(dcam.DCAM_IDPROP.SUBARRAYHSIZE, vsize)
        self.set_prop(dcam.DCAM_IDPROP.SUBARRAYVPOS, hpos)
        self.set_prop(dcam.DCAM_IDPROP.SUBARRAYHPOS, vpos)


    def get_ROI(self):
         hsize = int(self.get_prop(dcam.DCAM_IDPROP.SUBARRAYHSIZE))
        #  print(hsize)
         vsize = int(self.get_prop(dcam.DCAM_IDPROP.SUBARRAYVSIZE))
        #  print(vsize)
         hpos = int(self.get_prop(dcam.DCAM_IDPROP.SUBARRAYHPOS))
        #  print(hpos)
         vpos = int(self.get_prop(dcam.DCAM_IDPROP.SUBARRAYVPOS))
        #  print(vpos)
         return ((hpos, hpos+hsize), (vpos, vpos+vsize))

    def get_size(self):
        """Returns the size in pixels of the image being acquired. This is useful for checking the ROI settings.
        """
        X = int(self.get_prop(dcam.DCAM_IDPROP.SUBARRAYVSIZE))
        Y = int(self.get_prop(dcam.DCAM_IDPROP.SUBARRAYHSIZE))
        return X, Y

    def set_acquisition_mode(self, mode):
        self.mode = mode
        
    def set_exposure(self, exposure):
        """
        Sets the exposure of the camera.
        """
        self.exposure = exposure
        self.set_prop(dcam.DCAM_IDPROP.EXPOSURETIME, float(exposure.m_as('s')))

    def get_exposure(self):
        return self.get_prop(dcam.DCAM_IDPROP.EXPOSURETIME)

    def set_binning_4x4(self):
        self.set_prop(dcam.DCAM_IDPROP.BINNING, dcam.DCAMPROP.BINNING._4)
    
    def set_binning_1x1(self):
        self.set_prop(dcam.DCAM_IDPROP.BINNING, dcam.DCAMPROP.BINNING._1)

    def read_camera(self):
        if self.get_acquisition_mode() == BaseCamera.MODE_SINGLE_SHOT:
            return [self._snap()]
        elif self.get_acquisition_mode() == BaseCamera.MODE_CONTINUOUS:
            # print("waiting on frame...")
            assert self.camera.wait_capevent_frameready(-2147483648)
            transferinfo = self.camera.cap_transferinfo()
            assert (transferinfo is not False)
            # print("got frames! {}, {}".format(transferinfo.nFrameCount, transferinfo.nNewestFrameIndex))
            total_frame_count = transferinfo.nFrameCount
            #minus one here because if we've e.g. seen one frame and handled it, self.last_Frame = 0, and frame_count = 1, so backlog = 0
            backlog = total_frame_count - self.last_frame - 1
            #TODO(hayley): check this code for edge cases, like read/write conflicts by checking that the framestamp matches what we expect
            #TODO(hayley): possible optimization by preallocating and reusing the numpy buffers too
            if backlog >= self.n_buffers:
                print("Hamamatsu buffer overrun detected! Saw a backlog of {} frames while we have {} buffers".format(backlog, self.n_buffers))
                #simply restart from the last frame. This should be a rare occurence caused by intermittent long term interuppts
                self.last_frame_idx = transferinfo.nNewestFrameIndex
                self.last_frame = transferinfo.nFrameCount-1
                (aFrame, data) = self.camera.buf_getframe(transferinfo.nNewestFrameIndex)
                # print(aFrame.framestamp, aFrame.iFrame)
                return [(aFrame,data)]
            else:
                ret = [None]*backlog
                # print("backlog is {}, buffer is {}".format(backlog, ret))
                for i in range(0,backlog):
                    # print("trying to grab {}".format(self.last_frame_idx+1))
                    ret[i] = self.camera.buf_getframe(self.last_frame_idx+1)
                    self.last_frame_idx = self.last_frame_idx + 1 if self.last_frame_idx < self.n_buffers-2 else 0
                    self.last_frame += 1
                    # print("grabbed framestamp {} with our stamp {}".format(aFrame.framestamp, self.last_frame))
                return ret
                    
        else:
            assert False

    ##non standard functions
    def get_model(self):
        return self.camera.dev_getstring(dcam.DCAM_IDSTR.MODEL)
    
    def close(self):
        if self.camera.is_opened():
            self.camera.dev_close()
            Camera.ActiveCameras -= 1
            if Camera.ActiveCameras == 0:
                dcam.Dcamapi.uninit()

    #not needed as we don't use sofware triggers
    def trigger_camera(self):
        pass

    def get_prop(self, prop_id):
        ret = self.camera.prop_getvalue(prop_id)
        #TODO(hayley) handle with here lasterr()
        if ret is False:
            print(self.camera.lasterr())
            assert ret
        return ret
    
    def set_prop(self, prop_id, val):
        # print(self.camera.cap_status())
        ret = self.camera.prop_setvalue(prop_id, val)
        #TODO(hayley) handle with here lasterr()
        if ret is False:
            print(self.camera.lasterr())
            assert ret
        return ret
    
    def set_prop_unchecked(self, prop_id, val):
        # print(self.camera.cap_status())
        ret = self.camera.prop_setvalue(prop_id, val)
        #TODO(hayley) handle with here lasterr()
        # if ret is False:
        #     print(self.camera.lasterr())
        #     assert ret
        return ret

    def _snap(self):
        assert (self.mode == BaseCamera.MODE_SINGLE_SHOT)
        assert(self.running)
        self.camera.cap_snapshot()
        #NOTE(hayley): there exists DCAMWAIT_TIMEOUT_INFINITE but it doesn't seem to be present in the python api? pynta/controller/hamamatsuy/dcamapi4.py
        # using int min (0x800...) = -2147483648 seems to work and exists in the C API
        assert self.camera.wait_capevent_frameready(-2147483648)
        self.camera.cap_stop()
        return self.camera.buf_getlastframedata()

if __name__ == "__main__":
    import cv2
    import numpy as np
    import time
    def normalize_u16(data):
        return (data*(65535.0/np.max(data))).astype(np.uint16)

    cam = Camera(0)
    print("size of {} is {}".format(cam.get_model(), cam.get_max_size()));
    # cam.set_binning_4x4()
    print("exposure is {}, fps = {}".format(cam.get_exposure(), cam.get_prop(dcam.DCAM_IDPROP.INTERNALFRAMERATE)))
    cam.set_exposure(0.0001)
    print("exposure is {}, fps = {}".format(cam.get_exposure(), cam.get_prop(dcam.DCAM_IDPROP.INTERNALFRAMERATE)))
    cam.start_acquisition(cam.MODE_SINGLE_SHOT)
    shot = cam.read_camera()[-1]
    cam.stop_acquisition()

    cv2.imshow("single shot", normalize_u16(shot))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    print("adjusting ROI...")
    print(cam.set_ROI((1000,1004), (1000,1004)))
    cam.start_acquisition(cam.MODE_CONTINUOUS)
    print("exposure is {}, fps = {}".format(cam.get_exposure(), cam.get_prop(dcam.DCAM_IDPROP.INTERNALFRAMERATE)))
    time.sleep(1)
    shot = cam.read_camera()[-1]
    # cam.stop_acquisition()
    cv2.imshow("single shot", normalize_u16(shot))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    shot = cam.read_camera()[-1]
    # cam.stop_acquisition()
    cv2.imshow("single shot", normalize_u16(shot))
    cv2.waitKey(0)
    cv2.destroyAllWindows()