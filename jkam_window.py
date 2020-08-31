from enum import Enum
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QIcon
from ui_components.camerawindow_ui import Ui_CameraWindow


class ImagingMode(Enum):
    VIDEO = 0
    ABSORPTION = 1


class JKamWindow(QMainWindow, Ui_CameraWindow):

    def __init__(self):
        super(JKamWindow, self).__init__()
        self.setupUi(self)

        self.data = None

        self.frame_received_signal = self.camera_control_widget.frame_received_signal
        self.frame_received_signal.connect(self.on_capture)

        self.history_image_view = None
        self.imaging_mode = None
        self.camera_control_widget.absorption_radioButton.clicked.connect(self.set_mode)
        self.camera_control_widget.video_radioButton.clicked.connect(self.set_mode)
        self.set_mode()

        self.absorption_frame_count = 0
        self.atom_frame = None
        self.bright_frame = None
        self.dark_frame = None
        self.optical_density_frame = None
        self.atom_number_frame = None

    def set_mode(self):
        try:
            self.frame_received_signal.disconnect(self.capture_video)
        except TypeError:
            pass
        try:
            self.frame_received_signal.disconnect(self.capture_absorption)
        except TypeError:
            pass
        try:
            self.frame_received_signal.disconnect(self.on_capture)
        except TypeError:
            pass
        try:
            self.history_image_view.removeItem(self.history_widget.roi)
        except AttributeError:
            pass

        if self.camera_control_widget.video_radioButton.isChecked():
            self.view_stackedWidget.setCurrentIndex(0)
            self.history_image_view = self.videovieweditor.imageview
            self.history_widget.setup_figure(self.history_image_view)
            self.imaging_mode = ImagingMode.VIDEO
            self.frame_received_signal.connect(self.capture_video)
        elif self.camera_control_widget.absorption_radioButton.isChecked():
            self.history_image_view = self.absorption_view_widget.N_view_editor.imageview
            self.history_widget.setup_figure(self.history_image_view)
            self.view_stackedWidget.setCurrentIndex(1)
            self.imaging_mode = ImagingMode.ABSORPTION
            self.frame_received_signal.connect(self.capture_absorption)

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
        self.history_widget.analyze_signal.emit(self, image_view.getImageItem())

    def display_absorption_frame(self, frame):
        self.absorption_view_widget.process_frame(frame)
        image_view = self.absorption_view_widget.N_view_editor.imageview
        self.history_widget.analyze_signal.emit(self, image_view.getImageItem())

    def closeEvent(self, event):
        self.camera_control_widget.close()


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
