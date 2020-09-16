"""
JKam package provides a GUI interface to control  camera sensors especially for use in ultracold atomic imaging
applications. Software control of various types of sensors is supported through the JKamGenDriver class which acts
as an interface between the JKam package and a sensor specific driver.
Functionality includes video acquisition and softwar and setting up software and hardware triggering as well as
sensor exposure adjustments. There is also support for absorption imaging which includes the capture of three
frames and subsequent image processing.
Image can be saved and autosaved upon acquisition and processing.
Some basic image processing functionality is implemented such as region of area integration with background subtraction.
There are plans to implement a Gaussian fit analyzer.

Original program by Jonathan Kohler.
Updated by Justin Gerber (2020) - gerberja@berkeley.edu
"""

from enum import Enum
import sys
import ctypes
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QIcon
from ui_components.camerawindow_ui import Ui_CameraWindow


class ImagingMode(Enum):
    VIDEO = 0
    ABSORPTION = 1
    FLUORESCENCE = 2


class JKamWindow(QMainWindow, Ui_CameraWindow):
    # TODO: Documentation
    # TODO: Saving and storing of cameras and settings
    # TODO: Gaussian Fit Analysis
    # TODO: More default settings to load in Andordriver
    # TODO: Cleanup Andor arming (use proper serial number for example)
    # TODO: Get Andor triggering working when app is loaded.
    # TODO: ROI imaging/saving to save on data storage?
    """
    Camera GUI. Includes visualization of image captures, camera controls and trigger configuration,
    UI for saving and autosaving of imaging and some simple image analysis UI.
    """
    analyze_signal = pyqtSignal()
    all_frames_received_signal = pyqtSignal()

    def __init__(self):
        super(JKamWindow, self).__init__()
        self.setupUi(self)

        self.frame_received_signal = self.camera_control_widget.frame_received_signal
        self.frame_received_signal.connect(self.on_capture)

        self.absorption_view_widget.analysis_complete_signal.connect(self.on_all_frames_received)
        self.fluorescence_view_widget.analysis_complete_signal.connect(self.on_all_frames_received)
        self.analyze_signal.connect(self.roi_analyzer_widget.analyze)

        self.imaging_mode = None
        self.image_capture_buttonGroup.buttonClicked.connect(self.set_imaging_mode)
        self.camera_control_widget.started_signal.connect(self.lock_imaging_mode)
        self.camera_control_widget.stopped_signal.connect(self.unlock_imaging_mode)
        self.camera_control_widget.trigger_mode_toggled.connect(self.trigger_mode_changed)
        self.set_imaging_mode()

        self.savebox_widget.save_single_pushButton.clicked.connect(self.save_frames)
        self.video_frame = None

    def on_capture(self, frame):
        self.frame_received_signal.disconnect(self.on_capture)
        if self.imaging_mode == ImagingMode.VIDEO:
            self.display_video_frame(frame)
        elif self.imaging_mode == ImagingMode.ABSORPTION:
            self.display_absorption_frame(frame)
        elif self.imaging_mode == ImagingMode.FLUORESCENCE:
            self.display_fluorescence_frame(frame)
        self.frame_received_signal.connect(self.on_capture)

    def display_video_frame(self, frame):
        self.video_frame = frame
        image_view = self.videovieweditor.imageview
        image_view.setImage(self.video_frame, autoRange=False,
                            autoLevels=False, autoHistogramRange=False)
        self.on_all_frames_received()

    def display_absorption_frame(self, frame):
        self.absorption_view_widget.process_frame(frame)

    def display_fluorescence_frame(self, frame):
        self.fluorescence_view_widget.process_frame(frame)

    def on_all_frames_received(self):
        self.analyze_signal.emit()
        if self.verify_autosave():
            self.save_frames()

    def save_frames(self):
        if self.imaging_mode == ImagingMode.VIDEO:
            self.savebox_widget.save(self.video_frame)
        if self.imaging_mode == ImagingMode.ABSORPTION:
            atom_frame = self.absorption_view_widget.atom_frame
            bright_frame = self.absorption_view_widget.bright_frame
            dark_frame = self.absorption_view_widget.dark_frame
            self.savebox_widget.save(atom_frame, bright_frame, dark_frame)
        if self.imaging_mode == ImagingMode.FLUORESCENCE:
            atom_frame = self.fluorescence_view_widget.atom_frame
            ref_frame = self.fluorescence_view_widget.ref_frame
            self.savebox_widget.save(atom_frame, ref_frame)

    def toggle_roi_analyzer_enable(self):
        self.roi_analyzer_enable_signal.emit(self.roi_analyzer_checkBox.isChecked())

    def toggle_roi_analyzer_bg_subtract(self):
        self.roi_analyzer_bg_enable_signal.emit(self.roi_bg_subtract_checkBox.isChecked())

    def analyzer_window_closed(self):
        self.roi_analyzer_checkBox.setChecked(False)

    def set_imaging_mode(self):
        if self.video_mode_radioButton.isChecked():
            self.view_stackedWidget.setCurrentIndex(0)
            self.roi_analyzer_widget.set_imageview(self.videovieweditor.imageview)
            self.imaging_mode = ImagingMode.VIDEO
            self.savebox_widget.mode = self.savebox_widget.ModeType.SINGLE
        elif self.absorption_mode_radioButton.isChecked():
            self.view_stackedWidget.setCurrentIndex(1)
            self.roi_analyzer_widget.set_imageview(self.absorption_view_widget.N_view_editor.imageview)
            self.imaging_mode = ImagingMode.ABSORPTION
            self.savebox_widget.mode = self.savebox_widget.ModeType.ABSORPTION
        elif self.fluorescence_mode_radioButton.isChecked():
            self.view_stackedWidget.setCurrentIndex(2)
            self.roi_analyzer_widget.set_imageview(self.fluorescence_view_widget.N_view_editor.imageview)
            self.imaging_mode = ImagingMode.FLUORESCENCE
            self.savebox_widget.mode = self.savebox_widget.ModeType.FLUORESCENCE

    def lock_imaging_mode(self):
        self.video_mode_radioButton.setEnabled(False)
        self.absorption_mode_radioButton.setEnabled(False)
        self.fluorescence_mode_radioButton.setEnabled(False)

    def unlock_imaging_mode(self):
        self.video_mode_radioButton.setEnabled(True)
        if not self.camera_control_widget.continuous_radioButton.isChecked():
            self.absorption_mode_radioButton.setEnabled(True)
            self.fluorescence_mode_radioButton.setEnabled(True)

    def trigger_mode_changed(self):
        if self.camera_control_widget.continuous_radioButton.isChecked():
            self.video_mode_radioButton.setChecked(True)
            self.absorption_mode_radioButton.setEnabled(False)
            self.fluorescence_mode_radioButton.setEnabled(False)
        elif self.camera_control_widget.triggered_radioButton.isChecked():
            self.absorption_mode_radioButton.setEnabled(True)
            self.fluorescence_mode_radioButton.setEnabled(True)
        self.set_imaging_mode()

    def verify_autosave(self):
        if not self.camera_control_widget.continuous_radioButton.isChecked() and self.savebox_widget.autosaving:
            return True
        else:
            return False

    def closeEvent(self, event):
        self.camera_control_widget.close()
        sys.exit()


def main():
    app = QApplication(sys.argv)

    # Code to setup windows icon for jkam
    app.setWindowIcon(QIcon('favicon.png'))
    myappid = u'jkam_app'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    ex = JKamWindow()
    ex.show()
    app.exec_()


if __name__ == '__main__':
    main()
    sys.exit()
