"""
    Main Window
    ===========

    .. sectionauthor:: Aquiles Carattino <aquiles@aquicarattino.com>
"""

import os
import sys
import time
from datetime import datetime
from multiprocessing import Process

import h5py
import numpy as np
# import psutil
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.dockarea import DockArea, Dock
# from pynta.Model._session import _session
# from pynta.View.hdfloader import HDFLoader
from pynta.view.GUI.camera_viewer_widget import MonitorMainWidget
from pynta.view.GUI.old.waterfallWidget import waterfallWidget
from pynta.view.GUI.old.Monitor import popOutWindow
from pynta.view.GUI.old.messageWidget import messageWidget
from pynta.view.GUI.old.Monitor import specialTaskTracking

# from ...Model.workerSaver import workerSaver, clearQueue


pg.setConfigOptions(imageAxisOrder='row-major')

class MainWindow(QMainWindow):
    """
    Main control window for showing the live captured images and initiating special tasks
    """
    def __init__(self, experiment):
        """
        Inits the camera window

        :param experiment: Experiment that is controlled by the GUI
        """
        super().__init__()
        self.setWindowTitle('PyNTA: Python Nanoparticle Tracking Analysis')
        self.setMouseTracking(True)
        self.experiment = experiment
        self.area = DockArea()
        self.setCentralWidget(self.area)
        self.resize(1064, 840)
        self.area.setMouseTracking(True)

        # Main widget
        self.camWidget = MonitorMainWidget()
        self.camWidget.setup_cross_cut(self.experiment.max_height)
        self.camWidget.setup_cross_hair([self.experiment.max_width, self.experiment.max_height])
        self.camWidget.setup_roi_lines([self.experiment.max_width, self.experiment.max_height])
        self.camWidget.setup_mouse_tracking()

        self.messageWidget = messageWidget()

        self.cheatSheet = popOutWindow()



        self.dmainImage = Dock("Camera", size=(80, 35))  # sizes are in percentage
        self.dmainImage.addWidget(self.camWidget)
        self.area.addDock(self.dmainImage, 'right')
        self.dmessage = Dock("Messages", size=(40, 30))
        self.dmessage.addWidget(self.messageWidget)
        self.area.addDock(self.dmessage, 'right')

        # # Widget for displaying information to the user

        # # Small window to display the results of the special task
        # self.trajectoryWidget = trajectoryWidget()
        # # Window for the camera viewer
        # # self.camViewer = cameraViewer(self._session, self.camera, parent=self)
        # # Configuration widget with a parameter tree
        # # self.config = ConfigWidget(self._session)
        # # Line cut widget
        # self.crossCut = crossCutWindow(parent=self)
        # self.popOut = popOutWindow(parent=self) #_future: for making long message pop-ups
        # # Select settings Window
        # # self.selectSettings = HDFLoader()
        #
        self.refreshTimer = QtCore.QTimer()
        self.refreshTimer.timeout.connect(self.updateGUI)
        # self.refreshTimer.timeout.connect(self.crossCut.update)
        #
        self.refreshTimer.start(self.experiment.config['GUI']['refresh_time'])
        #
        # self.acquiring = False
        # self.logmessage = []
        #
        # ''' Initialize the camera and the camera related things '''
        # self.max_sizex = self.camera.GetCCDWidth()
        # self.max_sizey = self.camera.GetCCDHeight()
        # self.current_width = self.max_sizex
        # self.current_height = self.max_sizey
        #
        # # if self._session.Camera['roi_x1'] == 0:
        # #     self._session.Camera = {'roi_x1': 1}
        # # if self._session.Camera['roi_x2'] == 0 or self._session.Camera['roi_x2'] > self.max_sizex:
        # #     self._session.Camera = {'roi_x2': self.max_sizex}
        # # if self._session.Camera['roi_y1'] == 0:
        # #     self._session.Camera = {'roi_y1': 1}
        # # if self._session.Camera['roi_y2'] == 0 or self._session.Camera['roi_y2'] > self.max_sizey:
        # #     self._session.Camera = {'roi_y2': self.max_sizey}
        #
        # # self.config.populateTree(self.experiment.config)
        # self.lastBuffer = time.time()
        # self.lastRefresh = time.time()
        #
        # # Program variables
        # self.tempimage = []
        # self.bgimage = []
        # self.trackinfo = np.zeros((1,5)) # real particle trajectory filled by "LocateParticle" analysis
        # # self.noiselvl = self._session.Tracking['noise_level']
        # self.fps = 0
        # self.buffertime = 0
        # self.buffertimes = []
        # self.refreshtimes = []
        # self.totalframes = 0
        # self.droppedframes = 0
        # self.buffer_memory = 0
        # self.waterfall_data = []
        # self.watindex = 0 # Waterfall index
        # self.corner_roi = [] # Real coordinates of the corner of the ROI region. (Min_x and Min_y).
        # self.docks = []
        # # self.corner_roi.append(self._session.Camera['roi_x1'])
        # # self.corner_roi.append(self._session.Camera['roi_y1'])
        #
        # # Program status controllers
        # self.continuous_saving = False
        # self.show_waterfall = False
        # self.subtract_background = False
        # self.save_running = False
        # self.accumulate_buffer = False
        # self.specialtask_running = False
        # self.dock_state = None
        #
        self.setupActions()
        self.setupToolbar()
        self.setupMenubar()
        # self.setupDocks()
        # self.setupSignals()

        ### This block should erased in due time and one must rely exclusively on Session variables.
        # self.filedir = self._session.Saving['directory']
        # self.snap_filename = self._session.Saving['filename_photo']
        # self.movie_filename = self._session.Saving['filename_video']
        ###
        self.messageWidget.appendLog('i', 'Program started by %s' % self.experiment.config['User']['name'])

    def start_tracking(self):
        self.experiment.start_tracking()

    def showHelp(self):
        """To show the cheatsheet for shortcuts in a pop-up meassage box
        OBSOLETE, will be deleted after transferring info into a better message viewer!
        """
        self.experiment.plot_histogram()
        # msgBox = QtGui.QMessageBox()
        # msgBox.setIcon(QtGui.QMessageBox.Information)
        # msgBox.setText("Keyboard shortcuts and Hotkeys")
        # msgBox.setInformativeText("Press details for a full list")
        # msgBox.setWindowTitle("pynta CheatSheet")
        # msgBox.setDetailedText("""
        #     F1, Show cheatsheet\n
        #     F5, Snap image\n
        #     F6, Continuous run\n
        #     Alt+mouse: Select line \n
        #     Ctrl+mouse: Crosshair \n
        #     Ctrl+B: Toggle buffering\n
        #     Ctrl+G: Toggle background subtraction\n
        #     Ctrl+F: Empty buffer\n
        #     Ctrl+C: Start tracking\n
        #     Ctrl+V: Stop tracking\n
        #     Ctrl+M: Autosave on\n
        #     Ctrl+N: Autosave off\n
        #     Ctrl+S: Save image\n
        #     Ctrl+W: Start waterfall\n
        #     Ctrl+Q: Exit application\n
        #     Ctrl+Shift+W: Save waterfall data\n
        #     Ctrl+Shift+T: Save trajectory\n
        #     """)

    def setupActions(self):
        """Setups the actions that the program will have. It is placed into a function
        to make it easier to reuse in other windows.

        :rtype: None
        """
        self.exitAction = QtGui.QAction(QtGui.QIcon('pynta/View/GUI/Icons/power-icon.png'), '&Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.exitSafe)

        self.saveAction = QtGui.QAction(QtGui.QIcon('pynta/View/GUI/Icons/floppy-icon.png'),'&Save image',self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.setStatusTip('Save Image')
        self.saveAction.triggered.connect(self.saveImage)

        self.showHelpAction = QtGui.QAction(QtGui.QIcon('pynta/View/GUI/Icons/info-icon.png'),'Show cheatsheet',self)
        self.showHelpAction.setShortcut(QtCore.Qt.Key_F1)
        self.showHelpAction.setStatusTip('Show Cheatsheet')
        self.showHelpAction.triggered.connect(self.showHelp)
           
        self.saveWaterfallAction = QtGui.QAction("Save Waterfall", self)
        self.saveWaterfallAction.setShortcut('Ctrl+Shift+W')
        self.saveWaterfallAction.setStatusTip('Save waterfall data to new file')
        self.saveWaterfallAction.triggered.connect(self.saveWaterfall)

        self.saveTrajectoryAction = QtGui.QAction("Save Trajectory", self)
        self.saveTrajectoryAction.setShortcut('Ctrl+Shift+T')
        self.saveTrajectoryAction.setStatusTip('Save trajectory data to new file')
        self.saveTrajectoryAction.triggered.connect(self.saveTrajectory)

        self.snapAction = QtGui.QAction(QtGui.QIcon('pynta/View/GUI/Icons/snap.png'),'S&nap photo',self)
        self.snapAction.setShortcut(QtCore.Qt.Key_F5)
        self.snapAction.setStatusTip('Snap Image')
        self.snapAction.triggered.connect(self.snap)

        self.movieAction = QtGui.QAction(QtGui.QIcon('pynta/View/GUI/Icons/video-icon.png'),'Start &movie',self)
        self.movieAction.setShortcut(QtCore.Qt.Key_F6)
        self.movieAction.setStatusTip('Start Movie')
        self.movieAction.triggered.connect(self.startMovie)

        self.movieSaveStartAction = QtGui.QAction(QtGui.QIcon('pynta/View/GUI/Icons/Download-Database-icon.png'),'Continuous saves',self)
        self.movieSaveStartAction.setShortcut('Ctrl+M')
        self.movieSaveStartAction.setStatusTip('Continuous save to disk')
        self.movieSaveStartAction.triggered.connect(self.movieSave)

        self.movieSaveStopAction = QtGui.QAction(QtGui.QIcon('pynta/View/GUI/Icons/Delete-Database-icon.png'),'Stop continuous saves',self)
        self.movieSaveStopAction.setShortcut('Ctrl+N')
        self.movieSaveStopAction.setStatusTip('Stop continuous save to disk')
        self.movieSaveStopAction.triggered.connect(self.movieSaveStop)

        self.startWaterfallAction = QtGui.QAction(QtGui.QIcon('pynta/View/GUI/Icons/Blue-Waterfall-icon.png'),'Start &Waterfall',self)
        self.startWaterfallAction.setShortcut('Ctrl+W')
        self.startWaterfallAction.setStatusTip('Start Waterfall')
        self.startWaterfallAction.triggered.connect(self.startWaterfall)

        self.toggleBGAction = QtGui.QAction(QtGui.QIcon('pynta/View/GUI/Icons/noBg.png'), 'Toggle B&G-reduction', self)
        self.toggleBGAction.setShortcut('Ctrl+G')
        self.toggleBGAction.setStatusTip('Toggle Background Reduction')
        self.toggleBGAction.triggered.connect(self.start_tracking)

        self.setROIAction = QtGui.QAction(QtGui.QIcon('pynta/View/GUI/Icons/Zoom-In-icon.png'),'Set &ROI',self)
        self.setROIAction.setShortcut('Ctrl+T')
        self.setROIAction.setStatusTip('Set ROI')
        self.setROIAction.triggered.connect(self.getROI)

        self.clearROIAction = QtGui.QAction(QtGui.QIcon('pynta/View/GUI/Icons/Zoom-Out-icon.png'),'Set R&OI',self)
        self.clearROIAction.setShortcut('Ctrl+T')
        self.clearROIAction.setStatusTip('Clear ROI')
        self.clearROIAction.triggered.connect(self.clearROI)

        self.accumulateBufferAction = QtGui.QAction(QtGui.QIcon('pynta/View/GUI/Icons/disk-save.png'),'Accumulate buffer',self)
        self.accumulateBufferAction.setShortcut('Ctrl+B')
        self.accumulateBufferAction.setStatusTip('Start or stop buffer accumulation')
        self.accumulateBufferAction.triggered.connect(self.bufferStatus)

        self.clearBufferAction = QtGui.QAction('Clear Buffer',self)
        self.clearBufferAction.setShortcut('Ctrl+F')
        self.clearBufferAction.setStatusTip('Clears the buffer')
        self.clearBufferAction.triggered.connect(self.emptyQueue)

        self.viewerAction = QtGui.QAction('Start Viewer',self)
        # self.viewerAction.triggered.connect(self.camViewer.show)

        self.configAction = QtGui.QAction('Config Window',self)
        # self.configAction.triggered.connect(self.config.show)

        self.dockAction = QtGui.QAction('Restore Docks', self)
        self.dockAction.triggered.connect(self.setupDocks)

        self.crossCutAction = QtGui.QAction(QtGui.QIcon('pynta/View/GUI/Icons/Ruler-icon.png'),'Show cross cut', self)
        # self.crossCutAction.triggered.connect(self.crossCut.show)

        self.settingsAction = QtGui.QAction('Load config', self)
        # self.settingsAction.triggered.connect(self.selectSettings.show)

    def setupToolbar(self):
        """Setups the toolbar with the desired icons. It's placed into a function
        to make it easier to reuse in other windows.
        """
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(self.exitAction)
        self.toolbar2 = self.addToolBar('Image')
        self.toolbar2.addAction(self.saveAction)
        self.toolbar2.addAction(self.snapAction)
        self.toolbar2.addAction(self.crossCutAction)
        self.toolbar3 = self.addToolBar('Movie')
        self.toolbar3.addAction(self.movieAction)
        self.toolbar3.addAction(self.movieSaveStartAction)
        self.toolbar3.addAction(self.movieSaveStopAction)
        self.toolbar4 = self.addToolBar('Extra')
        self.toolbar4.addAction(self.startWaterfallAction)
        self.toolbar4.addAction(self.setROIAction)
        self.toolbar4.addAction(self.clearROIAction)
        self.toolbar4.addAction(self.clearROIAction)
        self.toolbar4.addAction(self.toggleBGAction)
        self.toolbar5 = self.addToolBar('Help')
        self.toolbar5.addAction(self.showHelpAction)

    def setupMenubar(self):
        """Setups the menubar.
        """
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(self.settingsAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.exitAction)
        self.snapMenu = menubar.addMenu('&Snap')
        self.snapMenu.addAction(self.snapAction)
        self.snapMenu.addAction(self.saveAction)
        self.movieMenu = menubar.addMenu('&Movie')
        self.movieMenu.addAction(self.movieAction)
        self.movieMenu.addAction(self.movieSaveStartAction)
        self.movieMenu.addAction(self.movieSaveStopAction)
        self.movieMenu.addAction(self.startWaterfallAction)
        self.configMenu = menubar.addMenu('&Configure')
        self.configMenu.addAction(self.toggleBGAction)
        self.configMenu.addAction(self.setROIAction)
        self.configMenu.addAction(self.clearROIAction)
        self.configMenu.addAction(self.accumulateBufferAction)
        self.configMenu.addAction(self.clearBufferAction)
        self.configMenu.addAction(self.viewerAction)
        self.configMenu.addAction(self.configAction)
        self.configMenu.addAction(self.dockAction)
        self.saveMenu = menubar.addMenu('S&ave')
        self.snapMenu.addAction(self.saveAction)
        self.saveMenu.addAction(self.saveWaterfallAction)
        self.saveMenu.addAction(self.saveTrajectoryAction)
        self.helpMenu = menubar.addMenu('&Help')
        self.helpMenu.addAction(self.showHelpAction)

    def setupDocks(self):
        """Setups the docks in order to recover the initial configuration if one gets closed."""

        for d in self.docks:
            try:
                d.close()
            except:
                pass

        self.docks = []

        self.dmainImage = Dock("Camera", size=(80, 35)) #sizes are in percentage
        self.dwaterfall = Dock("Waterfall", size=(80, 35))
        self.dparams = Dock("Parameters", size=(20, 100))
        self.dtraj = Dock("Trajectory", size=(40, 30))

        # self.dstatus = Dock("Status", size=(100, 3))

        self.area.addDock(self.dmainImage, 'right')
        self.area.addDock(self.dparams, 'left', self.dmainImage)
        self.area.addDock(self.dtraj, 'bottom', self.dmainImage)
        self.area.addDock(self.dmessage, 'right', self.dtraj)


        self.docks.append(self.dmainImage)
        self.docks.append(self.dtraj)
        self.docks.append(self.dmessage)
        self.docks.append(self.dparams)
        self.docks.append(self.dwaterfall)
        # self.area.addDock(self.dstatus, 'bottom', self.dparams)

        self.dmainImage.addWidget(self.camWidget)

        self.dparams.addWidget(self.config)
        self.dtraj.addWidget(self.trajectoryWidget)

        self.dock_state = self.area.saveState()

    def setupSignals(self):
        """Setups all the signals that are going to be handled during the excution of the program."""
        self.connect(self._session, QtCore.SIGNAL('updated'), self.config.populateTree)
        self.connect(self.config, QtCore.SIGNAL('updateSession'), self.updateSession)
        self.connect(self.camWidget, QtCore.SIGNAL('specialTask'), self.startSpecialTask)
        self.connect(self.camWidget, QtCore.SIGNAL('stopSpecialTask'), self.stopSpecialTask)
        self.connect(self.camViewer, QtCore.SIGNAL('stopMainAcquisition'), self.stopMovie)
        self.connect(self, QtCore.SIGNAL('stopChildMovie'), self.camViewer.stopCamera)
        self.connect(self, QtCore.SIGNAL('closeAll'), self.camViewer.closeViewer)
        self.connect(self.selectSettings, QtCore.SIGNAL("settings"), self.update_settings)
        self.connect(self, QtCore.SIGNAL('closeAll'), self.selectSettings.close)


    def snap(self):
        """Function for acquiring a single frame from the camera. It is triggered by the user.
        It gets the data the GUI will be updated at a fixed framerate.
        """
        if self.experiment.acquiring: #If it is itself acquiring a message is displayed to the user warning him
            msgBox = QtGui.QMessageBox()
            msgBox.setIcon(QtGui.QMessageBox.Critical)
            msgBox.setText("You cant snap a photo while in free run")
            msgBox.setInformativeText("The program is already acquiring data")
            msgBox.setWindowTitle("Already acquiring")
            msgBox.setDetailedText("""When in free run, you can\'t trigger another acquisition. \n
                You should stop the free run acquisition and then snap a photo.""")
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
            retval = msgBox.exec_()
            self.messageWidget.appendLog('e', 'Tried to snap while in free run')
        else:
            self.experiment.snap()
            # self.messageWidget.appendLog('i', 'Snapped photo')

    def toggleBGReduction(self):
        """Toggles between background cancellation modes. Takes a background snap if necessary
        """

        if self.subtract_background:
            self.subtract_background = False
            self.messageWidget.appendLog('i', 'Background reduction deactivated')
        else:
            if len(self.tempimage)==0:
                self.snap()
                self.messageWidget.appendLog('i', 'Snapped an image as background')
            else:
                self.subtract_background = True
                self.bgimage = self.tempimage.astype(float)
                self.messageWidget.appendLog('i', 'Background reduction active')

    def saveImage(self):
        """Saves the image that is being displayed to the user.
        """
        if len(self.tempimage) >= 1:
            # Data will be appended to existing file
            fn = self._session.Saving['filename_photo']
            filename = '%s.hdf5' % (fn)
            fileDir = self._session.Saving['directory']
            if not os.path.exists(fileDir):
                os.makedirs(fileDir)

            f = h5py.File(os.path.join(fileDir,filename), "a")
            now = str(datetime.now())
            g = f.create_group(now)
            dset = g.create_dataset('image', data=self.tempimage)
            meta = g.create_dataset('metadata',data=self._session.serialize())
            f.flush()
            f.close()
            self.messageWidget.appendLog('i', 'Saved photo')

    def startMovie(self):
        self.experiment.start_free_run()

    def stopMovie(self):
        if self.acquiring:
            self.workerThread.keep_acquiring = False
            while self.workerThread.isRunning():
                pass
            self.acquiring = False
            self.camera.stopAcq()
            self.messageWidget.appendLog('i', 'Continuous run stopped')
            if self.continuous_saving:
                self.movieSaveStop()

    def movieData(self):
        """Function just to trigger and read the camera in the separate thread.
        """
        self.workerThread.start()

    def movieSave(self):
        """Saves the data accumulated in the queue continuously.
        """
        if not self.continuous_saving:
            # Child process to save the data. It runs continuously until and exit flag
            # is passed through the Queue. (self.q.put('exit'))
            self.accumulate_buffer = True
            if len(self.tempimage) > 1:
                im_size = self.tempimage.nbytes
                max_element = int(self._session.Saving['max_memory']/im_size)
                #self.q = Queue(0)
            fn = self._session.Saving['filename_video']
            filename = '%s.hdf5' % (fn)
            fileDir = self._session.Saving['directory']
            if not os.path.exists(fileDir):
                os.makedirs(fileDir)
            to_save = os.path.join(fileDir, filename)
            metaData = self._session.serialize() # This prints a YAML-ready version of the session.
            self.p = Process(target=workerSaver, args=(to_save, metaData, self.q,))  #
            self.p.start()
            self.continuous_saving = True
            self.messageWidget.appendLog('i', 'Continuous autosaving started')
        else:
            self.messageWidget.appendLog('w', 'Continuous savings already triggered')

    def movieSaveStop(self):
        """Stops the saving to disk. It will however flush the queue.
        """
        if self.continuous_saving:
            self.q.put('Stop')
            self.accumulate_buffer = False
            #self.p.join()
            self.messageWidget.appendLog('i', 'Continuous autosaving stopped')
            self.continuous_saving = False

    def emptyQueue(self):
        """Clears the queue.
        """
        # Worker thread for clearing the queue.
        self.clearWorker = Process(target = clearQueue, args = (self.q,))
        self.clearWorker.start()

    def startWaterfall(self):
        """Starts the waterfall. The waterfall can be accelerated if camera supports hardware binning in the appropriate
        direction. If not, has to be done via software but the acquisition time cannot be improved.
        TODO: Fast waterfall should have separate window, since the acquisition of the full CCD will be stopped.
        """
        if not self.show_waterfall:
            self.watWidget = waterfallWidget()
            self.area.addDock(self.dwaterfall, 'bottom', self.dmainImage)
            self.dwaterfall.addWidget(self.watWidget)
            self.show_waterfall = True
            Sx, Sy = self.camera.getSize()
            self.waterfall_data = np.zeros((self._session.GUI['length_waterfall'], Sx))
            self.watWidget.img.setImage(np.transpose(self.waterfall_data), autoLevels=False, autoRange=False, autoHistogramRange=False)
            self.messageWidget.appendLog('i', 'Waterfall opened')
        else:
            self.closeWaterfall()

    def stopWaterfall(self):
        """Stops the acquisition of the waterfall.
        """
        pass

    def closeWaterfall(self):
        """Closes the waterfall widget.
        """
        if self.show_waterfall:
            self.watWidget.close()
            self.dwaterfall.close()
            self.show_waterfall = False
            del self.waterfall_data
            self.messageWidget.appendLog('i', 'Waterfall closed')

    def setROI(self, X, Y):
        """
        Gets the ROI from the lines on the image. It also updates the GUI to accommodate the changes.
        :param X:
        :param Y:
        :return:
        """
        if not self.acquiring:
            self.corner_roi[0] = X[0]
            self.corner_roi[1] = Y[0]
            if self._session.Debug['to_screen']:
                print('Corner: %s, %s' % (self.corner_roi[0], self.corner_roi[1]))
            self._session.Camera = {'roi_x1': int(X[0])}
            self._session.Camera = {'roi_x2': int(X[1])}
            self._session.Camera = {'roi_y1': int(Y[0])}
            self._session.Camera = {'roi_y2': int(Y[1])}
            self.messageWidget.appendLog('i', 'Updated roi_x1: %s' % int(X[0]))
            self.messageWidget.appendLog('i', 'Updated roi_x2: %s' % int(X[1]))
            self.messageWidget.appendLog('i', 'Updated roi_y1: %s' % int(Y[0]))
            self.messageWidget.appendLog('i', 'Updated roi_y2: %s' % int(Y[1]))

            Nx, Ny = self.camera.setROI(X, Y)
            Sx, Sy = self.camera.getSize()
            self.current_width = Sx
            self.current_height = Sy

            self.tempimage = np.zeros((Nx, Ny))
            self.camWidget.hline1.setValue(1)
            self.camWidget.hline2.setValue(Ny)
            self.camWidget.vline1.setValue(1)
            self.camWidget.vline2.setValue(Nx)
            self.trackinfo = np.zeros((1,5))
            #self.camWidget.img2.clear()
            if self.show_waterfall:
                self.waterfall_data = np.zeros((self._session.GUI['length_waterfall'], self.current_width))
                self.watWidget.img.setImage(np.transpose(self.waterfall_data))

            self.config.populateTree(self._session)
            self.messageWidget.appendLog('i', 'Updated the ROI')
        else:
            self.messageWidget.appendLog('e', 'Cannot change ROI while acquiring.')

    def getROI(self):
        """Gets the ROI coordinates from the GUI and updates the values."""
        y1 = np.int(self.camWidget.hline1.value())
        y2 = np.int(self.camWidget.hline2.value())
        x1 = np.int(self.camWidget.vline1.value())
        x2 = np.int(self.camWidget.vline2.value())
        X = np.sort((x1, x2))
        Y = np.sort((y1, y2))
        # Updates to the real values
        X += self.corner_roi[0] - 1
        Y += self.corner_roi[1] - 1
        self.setROI(X, Y)

    def clearROI(self):
        """Resets the roi to the full image.
        """
        if not self.acquiring:
            self.camWidget.hline1.setValue(1)
            self.camWidget.vline1.setValue(1)
            self.camWidget.vline2.setValue(self.max_sizex)
            self.camWidget.hline2.setValue(self.max_sizey)
            self.corner_roi = [1, 1]
            self.getROI()
        else:
            self.messageWidget.appendLog('e', 'Cannot change ROI while acquiring.')

    def bufferStatus(self):
        """Starts or stops the buffer accumulation.
        """
        if self.accumulate_buffer:
            self.accumulate_buffer = False
            self.messageWidget.appendLog('i', 'Buffer accumulation stopped')
        else:
            self.accumulate_buffer = True
            self.messageWidget.appendLog('i', 'Buffer accumulation started')

    def getData(self, data, origin):
        """Gets the data that is being gathered by the working thread.

        .. _getData:
        .. data: single image or a list of images (saved in buffer)
        .. origin: indicates which command has trigerred execution of this method (e.g. 'snap' of 'movie')
        both input variables are handed it through QThread signal that is "emit"ted
        """
        s = 0
        if origin == 'snap': # Single snap.
            self.acquiring=False
            self.workerThread.origin = None
            self.workerThread.keep_acquiring = False  # This already happens in the worker thread itself.
            self.camera.stopAcq()

        if isinstance(data, list):
            for d in data:
                if self.accumulate_buffer:
                    s = float(self.q.qsize())*int(d.nbytes)/1024/1024
                    if s<self._session.Saving['max_memory']:
                        self.q.put(d)
                    else:
                        self.droppedframes+=1

                if self.show_waterfall:
                    if self.watindex == self._session.GUI['length_waterfall']:
                        if self._session.Saving['autosave_trajectory']:
                            self.saveWaterfall()

                        self.waterfall_data = np.zeros((self._session.GUI['length_waterfall'], self.current_width))
                        self.watindex = 0

                    centerline = np.int(self.current_height / 2)
                    vbinhalf = np.int(self._session.GUI['vbin_waterfall'])
                    if vbinhalf >= self.current_height / 2 - 1:
                        wf = np.array([np.sum(d, 1)])
                    else:
                        wf = np.array([np.sum(d[:, centerline - vbinhalf:centerline + vbinhalf], 1)])
                    self.waterfall_data[self.watindex, :] = wf
                    self.watindex +=1
                self.totalframes+=1
            self.tempimage = d
        else:
            self.tempimage = data
            if self.accumulate_buffer:
                s = float(self.q.qsize())*int(data.nbytes)/1024/1024

                if s<self._session.Saving['max_memory']:
                    self.q.put(data)
                else:
                    self.droppedframes+=1

            if self.show_waterfall:
                if self.watindex == self._session.GUI['length_waterfall']:
                    # checks if the buffer variable for waterfall image is full, saves it if requested, and sets it to zero.
                    if self._session.Saving['autosave_trajectory']:
                        self.saveWaterfall()

                    self.waterfall_data = np.zeros((self._session.GUI['length_waterfall'], self.current_width))
                    self.watindex = 0

                centerline = np.int(self.current_height/2)
                vbinhalf = np.int(self._session.GUI['vbin_waterfall']/2)

                if vbinhalf >= self.current_height-1:
                    wf = np.array([np.sum(data,1)])
                else:
                    wf = np.array([np.sum(data[:,centerline-vbinhalf:centerline+vbinhalf], 1)])
                self.waterfall_data[self.watindex, :] = wf
                self.watindex +=1

            self.totalframes += 1

        new_time = time.time()
        self.buffertime = new_time - self.lastBuffer
        self.lastBuffer = new_time
        self.buffer_memory = s
        if self._session.Debug['queue_memory']:
            print('Queue Memory: %3.2f MB' % self.buffer_memory)

    def updateGUI(self):
        """Updates the image displayed to the user.
        """
        if self.experiment.temp_image is not None:
            img = self.experiment.temp_image
            self.camWidget.img.setImage(img.astype(int), autoLevels=False, autoRange=False, autoHistogramRange=False)
        if self.experiment.link_particles_running:
            self.camWidget.draw_target_pointer(self.experiment.localize_particles_image(img))


    def saveWaterfall(self):
        """Saves the waterfall data, if any.
        """
        if len(self.waterfall_data) > 1:
            fn = self._session.Saving['filename_waterfall']
            filename = '%s.hdf5' % (fn)
            fileDir = self._session.Saving['directory']
            if not os.path.exists(fileDir):
                os.makedirs(fileDir)

            f = h5py.File(os.path.join(fileDir,filename), "a")
            now = str(datetime.now())
            g = f.create_group(now)
            dset = g.create_dataset('waterfall', data=self.waterfall_data)
            meta = g.create_dataset('metadata', data=self._session.serialize().encode("ascii","ignore"))
            f.flush()
            f.close()
            self.messageWidget.appendLog('i','Saved Waterfall')

    def saveTrajectory(self):
        """Saves the trajectory data, if any.
        """
        if len(self.trackinfo) > 1:
            fn = self._session.Saving['filename_trajectory']
            filename = '%s.hdf5' % (fn)
            fileDir = self._session.Saving['directory']
            if not os.path.exists(fileDir):
                os.makedirs(fileDir)

            f = h5py.File(os.path.join(fileDir,filename), "a")
            now = str(datetime.now())
            g = f.create_group(now)
            dset = g.create_dataset('trajectory', data=[self.trackinfo])
            meta = g.create_dataset('metadata',data=self._session.serialize().encode("ascii","ignore"))
            f.flush()
            f.close()
            self.messageWidget.appendLog('i', 'Saved Trajectory')


    def update_settings(self, settings):
        new_session = _session(settings)
        self.updateSession(new_session)
        self.config.populateTree(self._session)

    def updateSession(self, session):
        """Updates the session variables passed by the config window.
        """
        update_cam = False
        update_roi = False
        update_exposure = False
        update_binning = True
        for k in session.params['Camera']:
            new_prop = session.params['Camera'][k]
            old_prop = self._session.params['Camera'][k]
            if new_prop != old_prop:
                update_cam = True
                if k in ['roi_x1', 'roi_x2', 'roi_y1', 'roi_y2']:
                    update_roi = True
                    if self._session.Debug['to_screen']:
                        print('Update ROI')
                elif k == 'exposure_time':
                    update_exposure = True
                elif k in ['binning_x', 'binning_y']:
                    update_binning = True

        if session.GUI['length_waterfall'] != self._session.GUI['length_waterfall']:
            if self.show_waterfall:
                self.closeWaterfall()
                self.restart_waterfall = True

        self.messageWidget.appendLog('i', 'Parameters updated')
        self.messageWidget.appendLog('i', 'Measurement: %s' % session.User['measurement'])
        self._session = session.copy()

        if update_cam:
            if self.acquiring:
                self.stopMovie()

            if update_roi:
                X = np.sort([session.Camera['roi_x1'], session.Camera['roi_x2']])
                Y = np.sort([session.Camera['roi_y1'], session.Camera['roi_y2']])
                self.setROI(X, Y)

            if update_exposure:
                new_exp = self.camera.setExposure(session.Camera['exposure_time'])
                self._session.Camera = {'exposure_time': new_exp}
                self.messageWidget.appendLog('i', 'Updated exposure: %s' % new_exp)
                if self._session.Debug['to_screen']:
                    print("New Exposure: %s" % new_exp)
                    print(self._session)

            if update_binning:
                self.camera.setBinning(session.Camera['binning_x'],session.Camera['binning_y'])

        self.refreshTimer.stop()
        self.refreshTimer.start(session.GUI['refresh_time'])


    def startSpecialTask(self):
        """Starts a special task. This is triggered by the user with a special combination of actions, for example clicking
        with the mouse on a plot, draggin a crosshair, etc."""
        if not self.specialtask_running:
            if self.acquiring:
                self.stopMovie()
                self.acquiring = False

            locy = self.camWidget.crosshair[0].getPos()[1]
            locx = self.camWidget.crosshair[1].getPos()[0]
            self.trackinfo = np.zeros((1,5))
            self.trajectoryWidget.plot.clear()
            imgsize = self.tempimage.shape
            iniloc = [locx, locy]
            self.specialTaskWorker = specialTaskTracking(self._session, self.camera, self.noiselvl, imgsize, iniloc)
            self.connect(self.specialTaskWorker,QtCore.SIGNAL('image'),self.getData)
            self.connect(self.specialTaskWorker,QtCore.SIGNAL('coordinates'),self.getParticleLocation)
            self.specialTaskWorker.start()
            self.specialtask_running = True
            self.messageWidget.appendLog('i', 'Live tracking started')
        else:
            print('Special task already running')

    def stopSpecialTask(self):
        """Stops the special task"""
        if self.specialtask_running:
            self.specialTaskWorker.keep_running = False
            self.specialtask_running = False
            if self._session.Saving['autosave_trajectory'] == True:
                self.saveTrajectory()
            self.messageWidget.appendLog('i', 'Live tracking stopped')

    def done(self):
        #self.saveRunning = False
        self.acquiring = False

    def exitSafe(self):
        self.close()

    def closeEvent(self,evnt):
        """
            Triggered at closing. Checks that the save is complete and closes the dataFile
        """
        self.experiment.finalize()

        # self.messageWidget.appendLog('i', 'Closing the program')
        # if self.acquiring:
        #     self.stopMovie()
        # if self.specialtask_running:
        #     self.stopSpecialTask()
        #     while self.specialTaskWorker.isRunning():
        #         pass
        # self.emit(QtCore.SIGNAL('closeAll'))
        # self.camera.stopCamera()
        # self.movieSaveStop()
        # try:
        #     # Checks if the process P exists and tries to close it.
        #     if self.p.is_alive():
        #         qs = self.q.qsize()
        #         with ProgressDialog("Finish saving data...", 0, qs) as dlg:
        #             while self.q.qsize() > 1:
        #                 dlg.setValue(qs - self.q.qsize())
        #                 time.sleep(0.5)
        #     self.p.join()
        # except AttributeError:
        #     pass
        # if self.q.qsize() > 0:
        #     self.messageWidget.appendLog('i', 'The queue was not empty')
        #     print('Freeing up memory...')
        #     self.emptyQueue()
        #
        # # Save LOG.
        # fn = self._session.Saving['filename_log']
        # timestamp = datetime.now().strftime('%H%M%S')
        # filename = '%s%s.log' % (fn, timestamp)
        # fileDir = self._session.Saving['directory']
        # if not os.path.exists(fileDir):
        #     os.makedirs(fileDir)
        #
        # f = open(os.path.join(fileDir,filename), "a")
        # for line in self.messageWidget.logText:
        #     f.write(line+'\n')
        # f.flush()
        # f.close()
        # print('Saved LOG')
        super(MainWindow, self).closeEvent(evnt)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    cam = MainWindow()
    cam.show()
    sys.exit(app.exec_())
