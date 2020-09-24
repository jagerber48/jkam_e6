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
import sys
import ctypes
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QIcon
from package.ui.camerawindow_ui import Ui_CameraWindow
from package.data.camerasettings import RbAtom
from package.widgets.imagecapturemodewidget import ImagingMode


class JKamWindow(QMainWindow, Ui_CameraWindow):
    # TODO: Documentation
    # TODO: Saving and storing of cameras and settings
    # TODO: Gaussian Fit Analysis
    # TODO: More default settings to load in Andordriver
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
        self.imagecapturemodewidget.state_set_signal.connect(self.set_imaging_mode)
        self.camera_control_widget.started_signal.connect(self.imagecapturemodewidget.started)
        self.camera_control_widget.continuous_enabled_signal.connect(self.imagecapturemodewidget.continuous_enabled)
        self.camera_control_widget.triggered_enabled_signal.connect(self.imagecapturemodewidget.triggered_enabled)
        self.camera_control_widget.disarmed_signal.connect(self.imagecapturemodewidget.disarmed)
        self.imagecapturemodewidget.set_imaging_mode()

        self.camera_control_widget.armed_signal.connect(self.armed)
        self.camera_control_widget.disarmed_signal.connect(self.disarmed)

        self.savebox_widget.save_single_pushButton.clicked.connect(self.save_frames)
        self.video_frame = None
        self.show()

    def on_capture(self, frame):
        self.frame_received_signal.disconnect(self.on_capture)
        if self.imaging_mode is ImagingMode.VIDEO:
            self.display_video_frame(frame)
        elif self.imaging_mode is ImagingMode.ABSORPTION:
            self.display_absorption_frame(frame)
        elif self.imaging_mode is ImagingMode.FLUORESCENCE:
            self.display_fluorescence_frame(frame)
        self.frame_received_signal.connect(self.on_capture)

    def display_video_frame(self, frame):
        self.video_frame = frame
        self.videovieweditor.setImage(self.video_frame, autoRange=False,
                                      autoLevels=False, autoHistogramRange=False)
        # image_view = self.videovieweditor.imageview
        # image_view.setImage(self.video_frame, autoRange=False,
        #                     autoLevels=False, autoHistogramRange=False)
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
        if self.imaging_mode is ImagingMode.VIDEO:
            self.savebox_widget.save(self.video_frame)
        if self.imaging_mode is ImagingMode.ABSORPTION:
            atom_frame = self.absorption_view_widget.atom_frame
            bright_frame = self.absorption_view_widget.bright_frame
            dark_frame = self.absorption_view_widget.dark_frame
            self.savebox_widget.save(atom_frame, bright_frame, dark_frame)
        if self.imaging_mode is ImagingMode.FLUORESCENCE:
            atom_frame = self.fluorescence_view_widget.atom_frame
            ref_frame = self.fluorescence_view_widget.ref_frame
            self.savebox_widget.save(atom_frame, ref_frame)

    def set_imaging_mode(self, imaging_mode):
        self.imaging_mode = imaging_mode
        if self.imaging_mode is ImagingMode.VIDEO:
            self.view_stackedWidget.setCurrentIndex(0)
            self.roi_analyzer_widget.set_imageview(self.videovieweditor.imageview)
            self.savebox_widget.mode = self.savebox_widget.ModeType.SINGLE
        elif self.imaging_mode is ImagingMode.ABSORPTION:
            self.view_stackedWidget.setCurrentIndex(1)
            self.roi_analyzer_widget.set_imageview(self.absorption_view_widget.N_view_editor.imageview)
            self.savebox_widget.mode = self.savebox_widget.ModeType.ABSORPTION
        elif self.imaging_mode is ImagingMode.FLUORESCENCE:
            self.view_stackedWidget.setCurrentIndex(2)
            self.roi_analyzer_widget.set_imageview(self.fluorescence_view_widget.N_view_editor.imageview)
            self.savebox_widget.mode = self.savebox_widget.ModeType.FLUORESCENCE

    def armed(self):
        imaging_system = self.camera_control_widget.imaging_system
        self.absorption_view_widget.load_analyzer(atom=RbAtom, imaging_system=imaging_system)

    def disarmed(self):
        self.absorption_view_widget.unload_analyzer()

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
