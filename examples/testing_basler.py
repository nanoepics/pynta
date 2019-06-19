#!/usr/bin/env python3
import faulthandler

faulthandler.enable()
import sys

sys.settrace
import os

os.environ["PYLON_CAMEMU"] = "3"
from pypylon import pylon
from pypylon import genicam
import time
import threading
import numpy

AVAILABLE_CAMERAS = [None, None]
# Camera default values:
EXPOSURE_TIME = 1000
GAIN = 0.0
CAMERA_BUFFER_SIZE = 1
ThreadLock = [threading.Lock(), threading.Lock()]


class AcquisitionThread(threading.Thread):
    def __init__(self, AppVars, Camera, FrateAvg):
        threading.Thread.__init__(self)
        self.AppVars = AppVars
        self.Camera = Camera
        self.Navg = FrateAvg
        self.Go = True
        self._run_event = threading.Event()
        self._run_event.set()

    def Resume(self):
        self._run_event.set()

    def Pause(self):
        self._run_event.clear()

    def Join(self):
        self.Go = False
        self.join(0.1)

    def run(self):
        try:
            Cam = self.Camera
            AvgFR = [0] * self.Navg
            Fcount = int(0)
            dT = 0
            T = time.time()
            Frame = self.AppVars.available_cameras[Cam].RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
            FrameID = Frame.GetID()
            Frame.Release()
            while self.Go:
                self._run_event.wait()
                Frame = self.AppVars.available_cameras[Cam].RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
                if not Frame.GrabSucceeded():
                    print('Grab failed')
                    continue
                if Frame.GetID() == FrameID:
                    print('Frame ID unchanged' + str(FrameID))
                    continue
                FrameID = Frame.GetID()
                frm = Frame.GetArray()
                Frame.Release()
                dT = time.time() - T
                T = time.time()
                AvgFR[Fcount % self.Navg] = dT
                #                ThreadLock[Cam].acquire()
                #                self.AppVars.FrameID[Cam] = FrameID
                #                self.AppVars.frame[Cam] = frm.copy()
                #                self.AppVars.FrameRate[Cam] = 1 / (sum(AvgFR) / len(AvgFR))
                #                ThreadLock[Cam].release()
                Fcount += 1
        except genicam.GenericException as e:
            print("An exception occurred.", e.GetDescription())
        finally:
            print("AcquisitionThread error camera " + str(Cam))


class Application:
    def __init__(self):
        self.FrameRate = [0, 0]
        self.frame = [None, None]
        self.FrameID = [None, None]
        self.available_cameras = [None, None]
        self.CameraList_str = [None, None]
        self.ExposureT = EXPOSURE_TIME
        self.CamThread = [None, None]
        self.Ncams = 0

    def find_cameras(self):
        tlFactory = pylon.TlFactory.GetInstance()
        devices = tlFactory.EnumerateDevices()
        for i, d in enumerate(devices):
            dev = pylon.InstantCamera(tlFactory.CreateDevice(devices[i]))
            if dev.IsUsb():
                self.available_cameras[self.Ncams] = dev
                self.CameraList_str.append(str(self.Ncams) + ": " + dev.GetDeviceInfo().GetFriendlyName())
                self.Ncams += 1
            if self.Ncams == 2:
                break

    def camera_init(self):
        for ic in range(self.Ncams):
            self.available_cameras[ic].Open()
            self.available_cameras[ic].OutputQueueSize = CAMERA_BUFFER_SIZE
            self.available_cameras[ic].ExposureTime.SetValue(self.ExposureT)
            self.available_cameras[ic].StartGrabbing()

    #            self.available_cameras[ic].StartGrabbing(pylon.GrabStrategy_LatestImages)

    def start_acuisition(self):
        self.find_cameras()
        self.camera_init()
        for ic in range(self.Ncams):
            self.CamThread[ic] = AcquisitionThread(self, ic, 10)
            self.CamThread[ic].start()
        i = 0
        while self.available_cameras[0].IsGrabbing():
            None


App = Application()
App.start_acuisition()
