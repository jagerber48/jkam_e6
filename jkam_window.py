from enum import Enum
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QIcon
from ui_components.camerawindow_ui import Ui_CameraWindow
from AnalysisWidgets import PlotHistoryAnalyzer, RoiIntegrationAnalyzer


class ImagingMode(Enum):
    VIDEO = 0
    ABSORPTION = 1


class JKamWindow(QMainWindow, Ui_CameraWindow):
    # TODO: Documentation
    # TODO: Handle closing of analysis window
    # TODO: Saving and storing of cameras and settings
    # TODO: Gaussian Fit Analysis
    # TODO: Implement Fluorescence Imaging
    """
    GUI to control cameras especially for use in ultracold atomic imaging applications. Software control of
    different types of commercial imaging sensors. Provides functionality for video capture as well as multi-image
    capture and processing. Also includes rudimentary image analysis tools such as region of interest integration
    and (future) gaussian fits.
    """

    def __init__(self):
        super(JKamWindow, self).__init__()
        self.setupUi(self)

        self.frame_received_signal = self.camera_control_widget.frame_received_signal
        self.frame_received_signal.connect(self.on_capture)

        self.plothistoryanalyzer = PlotHistoryAnalyzer(RoiIntegrationAnalyzer(self.videovieweditor.imageview))
        self.roi_analyzer_checkBox.clicked.connect(self.toggle_analyzer_window)
        self.roi_bg_subtract_checkBox.toggled.connect(self.bg_subtract_toggled)
        self.absorption_view_widget.analyis_complete_signal.connect(self.analyze)

        self.imaging_mode = None
        self.video_mode_radioButton.clicked.connect(self.set_imaging_mode)
        self.absorption_mode_radioButton.clicked.connect(self.set_imaging_mode)
        self.camera_control_widget.started_signal.connect(self.lock_imaging_mode)
        self.camera_control_widget.stopped_signal.connect(self.unlock_imaging_mode)
        self.camera_control_widget.trigger_mode_toggled.connect(self.trigger_mode_changed)
        self.set_imaging_mode()

    def bg_subtract_toggled(self):
        if self.roi_bg_subtract_checkBox.isChecked():
            self.plothistoryanalyzer.analyzer.enable_bg_subtract()
        if not self.roi_bg_subtract_checkBox.isChecked():
            self.plothistoryanalyzer.analyzer.disable_bg_subtract()

    def on_capture(self, frame):
        self.frame_received_signal.disconnect(self.on_capture)
        if self.imaging_mode == ImagingMode.VIDEO:
            self.display_video_frame(frame)
        elif self.imaging_mode == ImagingMode.ABSORPTION:
            self.display_absorption_frame(frame)
        self.frame_received_signal.connect(self.on_capture)

    def display_video_frame(self, frame):
        image_view = self.videovieweditor.imageview
        image_view.setImage(frame, autoRange=False,
                            autoLevels=False, autoHistogramRange=False)
        self.analyze()

    def display_absorption_frame(self, frame):
        self.absorption_view_widget.process_frame(frame)

    def analyze(self):
        self.plothistoryanalyzer.analysis_request_signal.emit()

    def toggle_analyzer_window(self):
        if self.roi_analyzer_checkBox.isChecked():
            self.plothistoryanalyzer.plothistorywidget.show()
            self.plothistoryanalyzer.enable()
        else:
            self.plothistoryanalyzer.plothistorywidget.close()
            self.plothistoryanalyzer.disable()

    def set_imaging_mode(self):
        if self.video_mode_radioButton.isChecked():
            self.view_stackedWidget.setCurrentIndex(0)
            self.plothistoryanalyzer.analyzer.set_imageview(self.videovieweditor.imageview)
            self.imaging_mode = ImagingMode.VIDEO
        elif self.absorption_mode_radioButton.isChecked():
            self.view_stackedWidget.setCurrentIndex(1)
            self.plothistoryanalyzer.analyzer.set_imageview(self.absorption_view_widget.N_view_editor.imageview)
            self.imaging_mode = ImagingMode.ABSORPTION

    def lock_imaging_mode(self):
        self.video_mode_radioButton.setEnabled(False)
        self.absorption_mode_radioButton.setEnabled(False)

    def unlock_imaging_mode(self):
        self.video_mode_radioButton.setEnabled(True)
        if not self.camera_control_widget.continuous_radioButton.isChecked():
            self.absorption_mode_radioButton.setEnabled(True)

    def trigger_mode_changed(self):
        if self.camera_control_widget.continuous_radioButton.isChecked():
            self.video_mode_radioButton.setChecked(True)
            self.absorption_mode_radioButton.setChecked(False)
            self.absorption_mode_radioButton.setEnabled(False)
        elif self.camera_control_widget.triggered_radioButton.isChecked():
            self.absorption_mode_radioButton.setEnabled(True)
        self.set_imaging_mode()

    def closeEvent(self, event):
        self.camera_control_widget.close()
        sys.exit()


# Start Qt event loop unless running in interactive mode.
def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('favicon.ico'))
    ex = JKamWindow()
    ex.show()
    app.exec_()


if __name__ == '__main__':
    main()
    sys.exit()
