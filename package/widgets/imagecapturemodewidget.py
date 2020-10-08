from enum import Enum
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
from package.ui.imagecapturemodewidget_ui import Ui_ImageCaptureModeWidget


class ImagingMode(Enum):
    VIDEO = 0
    ABSORPTION = 1
    FLUORESCENCE = 2
    MULTISHOT = 3


class ImageCaptureModeWidget(QWidget, Ui_ImageCaptureModeWidget):
    state_set_signal = pyqtSignal(object)

    def __init__(self, parent=None):
        super(ImageCaptureModeWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.imaging_mode = ImagingMode.VIDEO
        self.image_capture_buttonGroup.buttonClicked.connect(self.set_imaging_mode)
        self.multishot_spinBox.valueChanged.connect(self.spinbox_adjusted)
        self.set_imaging_mode()

    def set_imaging_mode(self):
        if self.video_mode_radioButton.isChecked():
            self.imaging_mode = ImagingMode.VIDEO
        elif self.absorption_mode_radioButton.isChecked():
            self.imaging_mode = ImagingMode.ABSORPTION
        elif self.fluorescence_mode_radioButton.isChecked():
            self.imaging_mode = ImagingMode.FLUORESCENCE
        elif self.multishot_mode_radioButton.isChecked():
            self.imaging_mode = ImagingMode.MULTISHOT
        self.multishot_spinBox.setStyleSheet("QLineEdit {background-color: #FFFFFF;}")
        self.state_set_signal.emit(self.imaging_mode)

    def continuous_enabled(self):
        self.video_mode_radioButton.setEnabled(True)
        self.absorption_mode_radioButton.setEnabled(False)
        self.fluorescence_mode_radioButton.setEnabled(False)
        self.multishot_mode_radioButton.setEnabled(False)
        self.multishot_spinBox.setEnabled(False)
        self.video_mode_radioButton.setChecked(True)
        self.imaging_mode = ImagingMode.VIDEO
        self.state_set_signal.emit(self.imaging_mode)

    def triggered_enabled(self):
        self.video_mode_radioButton.setEnabled(True)
        self.absorption_mode_radioButton.setEnabled(True)
        self.fluorescence_mode_radioButton.setEnabled(True)
        self.multishot_mode_radioButton.setEnabled(True)
        self.multishot_spinBox.setEnabled(True)


    def started(self):
        self.video_mode_radioButton.setEnabled(False)
        self.absorption_mode_radioButton.setEnabled(False)
        self.fluorescence_mode_radioButton.setEnabled(False)
        self.multishot_mode_radioButton.setEnabled(False)
        self.multishot_spinBox.setEnabled(False)


    def disarmed(self):
        self.video_mode_radioButton.setEnabled(True)
        self.absorption_mode_radioButton.setEnabled(True)
        self.fluorescence_mode_radioButton.setEnabled(True)
        self.multishot_mode_radioButton.setEnabled(True)
        self.multishot_spinBox.setEnabled(True)

    def spinbox_adjusted(self):
        self.multishot_spinBox.setStyleSheet("QSpinBox {background-color: #FFAAAA;}")

