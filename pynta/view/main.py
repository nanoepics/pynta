from time import sleep

import numpy as np

from pynta.view.GUI.main_window import MainWindowGUI
from pynta.view.subscriber_thread import SubscriberThread


class MainWindow(MainWindowGUI):
    def __init__(self, experiment):
        """

        :param pynta.model.experiment.win_nanocet.NanoCET experiment: Experiment class
        """
        super().__init__(experiment.config['GUI']['refresh_time'])

        self.experiment = experiment
        self.camera_viewer_widget.setup_roi_lines([self.experiment.max_width, self.experiment.max_height])
        self.config_tracking_widget.update_config(self.experiment.config['tracking'])
        self.config_widget.update_config(self.experiment.config)
        self.tracking = False

        self.update_histogram_worker = SubscriberThread(self.experiment.publisher.port, 'histogram')
        self.update_histogram_worker.data_received.connect(self.update_histogram)
        self.update_histogram_worker.start()

    def initialize_camera(self):
        self.experiment.initialize_camera()

    def snap(self):
        self.experiment.snap()

    def update_gui(self):
        if self.experiment.temp_image is not None:
            self.camera_viewer_widget.update_image(self.experiment.temp_image)
            if self.experiment.tracking:
                locations = self.experiment.temp_locations
                self.camera_viewer_widget.draw_target_pointer(locations)

    def start_movie(self):
        if self.experiment.free_run_running:
            self.stop_movie()
            return
        self.experiment.start_free_run()
        self.actionStart_Movie.setToolTip('Stop Movie')

    def stop_movie(self):
        self.experiment.stop_free_run()
        self.actionStart_Movie.setToolTip('Start Movie')

    def set_roi(self):
        self.refresh_timer.stop()
        X, Y = self.camera_viewer_widget.get_roi_values()
        self.experiment.set_roi(X, Y)
        X, Y = self.experiment.camera.X, self.experiment.camera.Y
        X[1] += 1
        Y[1] += 1
        self.camera_viewer_widget.set_roi_lines(X, Y)
        self.refresh_timer.start()

    def clear_roi(self):
        self.refresh_timer.stop()
        self.experiment.clear_roi()
        self.camera_viewer_widget.set_roi_lines([0, self.experiment.max_width], [0, self.experiment.max_height])
        self.refresh_timer.start()

    def save_image(self):
        self.experiment.save_image()

    def start_continuous_saves(self):
        if self.experiment.save_stream_running:
            self.stop_continuous_saves()
            return

        self.experiment.save_stream()
        self.actionStart_Continuous_Saves.setToolTip('Stop Continuous Saves')

    def stop_continuous_saves(self):
        self.experiment.stop_save_stream()
        self.actionStart_Continuous_Saves.setToolTip('Start Continuous Saves')

    def start_tracking(self):
        self.experiment.start_tracking()
        self.tracking = True

    def start_saving_tracks(self):
        self.experiment.start_saving_location()

    def stop_saving_tracks(self):
        self.experiment.stop_saving_location()

    def start_linking(self):
        if self.experiment.link_particles_running:
            self.stop_linking()
            return
        self.experiment.start_linking_locations()
        self.actionStart_Linking.setToolTip('Stop Linking')

    def stop_linking(self):
        self.experiment.stop_linking_locations()
        self.actionStart_Linking.setToolTip('Start Linking')

    def calculate_histogram(self):
        if not self.experiment.location.calculating_histograms:
            self.experiment.location.calculate_histogram()

    def update_histogram(self, values):
        if len(values) > 0:
            vals = np.array(values)[:, 0]
            vals = vals[~np.isnan(vals)]
            self.histogram_tracks_widget.histogram_widget.update_distribution(vals)

    def update_tracks(self):
        locations = self.experiment.location.relevant_tracks()
        self.histogram_tracks_widget.tracks_widget.plot_trajectories(locations)

    def update_tracking_config(self, config):
        config = dict(
            tracking=config
        )
        self.experiment.update_config(**config)

    def update_config(self, config):
        self.experiment.update_config(**config)

    def closeEvent(self, *args, **kwargs):
        self.experiment.finalize()
        sleep(1)
        super().closeEvent(*args, **kwargs)

