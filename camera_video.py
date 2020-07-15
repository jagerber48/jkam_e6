import numpy as np
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QIcon
from camerawindow_ui import Ui_CameraWindow

cross_section = 2.91e-11
cam_pixel_size = 6.45e-6
magnification = 0.36


class CameraWindow(QMainWindow, Ui_CameraWindow):
    grasshopper_sn = '17491535'

    def __init__(self):
        super(CameraWindow, self).__init__()
        self.setupUi(self)

        self.driver = self.camera_control_widget.driver
        self.data = None

        self.history_image_view = None
        self.camera_control_widget.start_pushButton.clicked.connect(self.set_mode)

        self.absorption_frame_count = 0
        self.atom_frame = None
        self.bright_frame = None
        self.dark_frame = None
        self.optical_density_frame = None
        self.atom_number_frame = None

    def set_mode(self):
        try:
            self.driver.captured_signal.disconnect(self.capture_absorption)
        except TypeError:
            pass
        try:
            self.driver.captured_signal.disconnect(self.capture_video)
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
            self.driver.captured_signal.connect(self.capture_video)
        elif self.camera_control_widget.absorption_radioButton.isChecked():
            self.driver.captured_signal.connect(self.capture_absorption)
            self.history_image_view = self.absorption_view_widget.N_view_editor.imageview
            self.history_widget.setup_figure(self.history_image_view)
            self.view_stackedWidget.setCurrentIndex(1)

    def capture_video(self, image):
        if self.driver.acquiring:
            self.driver.captured_signal.disconnect(self.capture_video)
            self.data = image
            image_view = self.videovieweditor.imageview
            image_view.setImage(self.data, autoRange=False,
                                           autoLevels=False, autoHistogramRange=False)
            self.history_widget.analyze_signal.emit(self, image_view.getImageItem())
            self.driver.captured_signal.connect(self.capture_video)

    def capture_absorption(self, image):
        self.absorption_frame_count += 1
        if self.absorption_frame_count == 1:
            self.atom_frame = image
            image_view = self.absorption_view_widget.atom_view_editor.imageview
            image_view.setImage(image, autoRange=False, autoLevels=False, autoHistogramRange=False)
        elif self.absorption_frame_count == 2:
            self.bright_frame = image
            image_view = self.absorption_view_widget.bright_view_editor.imageview
            image_view.setImage(image, autoRange=False, autoLevels=False, autoHistogramRange=False)
        elif self.absorption_frame_count == 3:
            self.dark_frame = image
            image_view = self.absorption_view_widget.dark_view_editor.imageview
            image_view.setImage(image, autoRange=False, autoLevels=False, autoHistogramRange=False)
            self.process_absorption()
            image_view = self.absorption_view_widget.OD_view_editor.imageview
            image_view.setImage(self.optical_density_frame, autoRange=False, autoLevels=False,
                                autoHistogramRange=False)
            image_view = self.absorption_view_widget.N_view_editor.imageview
            image_view.setImage(self.atom_number_frame, autoRange=False, autoLevels=False,
                                autoHistogramRange=False)
            self.history_widget.analyze_signal.emit(self, image_view.getImageItem())
            self.absorption_frame_count = 0
        else:
            print('ERROR: too many frames')
            self.atom_frame = None
            self.bright_frame = None
            self.dark_frame = None
            self.absorption_frame_count = 0

    def process_absorption(self):
        numerator = self.atom_frame - self.dark_frame
        denominator = self.bright_frame - self.dark_frame

        # Set output to nan when dividing by zero
        ratio = np.true_divide(numerator, denominator,
                               out=np.full_like(numerator, 0, dtype=float), where=(denominator != 0))
        self.optical_density_frame = -1 * np.log(ratio, out=np.full_like(numerator, np.nan, dtype=float), where=ratio > 0)
        self.atom_number_frame = (self.optical_density_frame / cross_section
                                  * (cam_pixel_size / magnification) ** 2)

    def closeEvent(self, event):
        self.driver.close_connection()


# Start Qt event loop unless running in interactive mode.
def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('favicon.ico'))
    ex = CameraWindow()
    ex.show()
    app.exec_()


if __name__ == '__main__':
    main()
    sys.exit()
