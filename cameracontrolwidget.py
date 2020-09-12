from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from ui_components.cameracontrolwidget_ui import Ui_CameraControlWidget
from grasshopperdriver import GrasshopperDriver
from andordriver import AndorDriver


class CameraControlWidget(QWidget, Ui_CameraControlWidget):
    """
    This widget essentially serves as a ui for a jkamgendriver. It handles receiving user inputs to change camera
    settings such as camera state (arm/disarm, start/stop acquisition), trigger mode, and exposure time. It also
    receives and passes frames through the frame_received_signal signal.
    """
    grasshopper_sn = '17491535'  # Spare Camera for testing
    # grasshopper_sn = '18431942'  # Side Imaging
    frame_received_signal = pyqtSignal(object)
    started_signal = pyqtSignal()
    stopped_signal = pyqtSignal()
    trigger_mode_toggled = pyqtSignal()

    def __init__(self, parent=None):
        super(CameraControlWidget, self).__init__(parent=parent)
        self.setupUi(self)
        # self.driver = GrasshopperDriver()
        self.driver = AndorDriver()

        self.exposure_time = round(float(self.exposure_lineEdit.text()), 2)

        self.arm_pushButton.clicked.connect(self.toggle_arm)
        self.start_pushButton.clicked.connect(self.toggle_start)
        self.exposure_lineEdit.editingFinished.connect(self.update_exposure)
        self.exposure_pushButton.clicked.connect(self.set_exposure)
        self.triggered_radioButton.clicked.connect(self.toggle_trigger_mode)
        self.continuous_radioButton.clicked.connect(self.toggle_trigger_mode)
        self.software_trigger_radioButton.clicked.connect(self.toggle_trigger_source)
        self.hardware_trigger_radioButton.clicked.connect(self.toggle_trigger_source)
        self.software_trigger_pushButton.clicked.connect(self.driver.execute_software_trigger)
        self.driver.frame_captured_signal.connect(self.frame_received_signal.emit)

    def arm(self):
        serial_number = self.grasshopper_sn
        try:
            self.driver.arm_camera(serial_number)
            self.serial_label.setText(f'Serial Number: {serial_number}')
            self.arm_pushButton.setChecked(True)
            self.arm_pushButton.setText('Disarm Camera')
            self.start_pushButton.setEnabled(True)
            self.exposure_pushButton.setEnabled(True)
            self.set_exposure()
            self.enable_trigger_controls()
            self.toggle_trigger_mode()
        except Exception as e:
            print('Error while trying to ARM camera')
            print(e)
            self.abort()

    def disarm(self, aborting=False):
        if not aborting:
            try:
                if self.driver.acquiring:
                    self.stop()
                self.driver.disarm_camera()
            except Exception as e:
                print('Error while trying to DISARM camera')
                print(e)
                self.abort()
        self.serial_label.setText(f'Serial Number: xxxxxxxx')
        self.arm_pushButton.setChecked(False)
        self.arm_pushButton.setText('Arm Camera')
        self.start_pushButton.setEnabled(False)
        self.exposure_pushButton.setEnabled(False)
        self.disable_trigger_controls()

    def toggle_arm(self):
        if not self.driver.armed:
            self.arm()
        else:
            self.disarm()

    def start(self):
        try:
            self.driver.start_acquisition()
            self.start_pushButton.setText('Stop Camera')
            self.disable_trigger_controls()
            if self.triggered_radioButton.isChecked() and self.software_trigger_radioButton.isChecked():
                self.software_trigger_pushButton.setEnabled(True)
            self.started_signal.emit()
        except Exception as e:
            print('Error while trying to START video')
            print(e)
            self.abort()

    def stop(self, aborting=False):
        print('STOPPING')
        if not aborting:
            try:
                self.driver.stop_acquisition()
            except Exception as e:
                print('Error while trying to STOP video')
                print(e)
                self.abort()
        self.start_pushButton.setText('Start Camera')
        self.enable_trigger_controls()
        self.software_trigger_pushButton.setEnabled(False)
        self.stopped_signal.emit()

    def toggle_start(self):
        if not self.driver.acquiring:
            self.start()
        else:
            self.stop()

    def toggle_trigger_mode(self):
        self.trigger_mode_toggled.emit()
        if self.continuous_radioButton.isChecked():
            self.driver.trigger_off()
            self.toggle_source_controls(False)
        elif self.triggered_radioButton.isChecked():
            self.driver.trigger_on()
            self.toggle_source_controls(True)

    def toggle_trigger_source(self):
        if self.hardware_trigger_radioButton.isChecked():
            self.driver.set_hardware_trigger()
        elif self.software_trigger_radioButton.isChecked():
            self.driver.set_software_trigger()

    def enable_trigger_controls(self):
        self.continuous_radioButton.setEnabled(True)
        self.triggered_radioButton.setEnabled(True)
        if self.triggered_radioButton.isChecked():
            self.toggle_source_controls(True)

    def disable_trigger_controls(self):
        self.continuous_radioButton.setEnabled(False)
        self.triggered_radioButton.setEnabled(False)
        self.toggle_source_controls(False)

    def toggle_source_controls(self, toggle_value):
        self.software_trigger_radioButton.setEnabled(toggle_value)
        self.hardware_trigger_radioButton.setEnabled(toggle_value)

    def update_exposure(self):
        exposure_input = self.exposure_lineEdit.text()
        try:
            self.exposure_time = round(float(exposure_input), 2)
        except ValueError:
            print(f'{exposure_input} invalid input for exposure time')
            self.exposure_lineEdit.setText(f'{self.exposure_time:.2f}')

    def set_exposure(self):
        self.driver.set_exposure_time(self.exposure_time)

    def abort(self):
        self.stop(aborting=True)
        self.disarm(aborting=True)

    def close(self):
        self.driver.close_connection()
