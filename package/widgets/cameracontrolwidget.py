from enum import Enum
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSignal
from package.ui.cameracontrolwidget_ui import Ui_CameraControlWidget
from package.data import camerasettings


class CaptureMode(Enum):
    TRIGGERED = 0
    CONTINUOUS = 1


class TriggerSource(Enum):
    HARDWARE = 0
    SOFTWARE = 1


class ArmMode(Enum):
    DISARMED = 0
    ARMED = 1


class AcquireMode(Enum):
    STOPPED = 0
    STARTED = 1


class CameraControlWidget(QWidget, Ui_CameraControlWidget):
    # TODO: Calls to JKamGenDriver could be done through signals so that JKamGenDriver could operate in its own thread
    """
    This widget essentially serves as a ui for a jkamgendriver. It handles receiving user inputs to change camera
    settings such as camera state (arm/disarm, start/stop acquisition), trigger mode, and exposure time. It also
    receives and passes frames through the frame_received_signal signal.
    """
    frame_received_signal = pyqtSignal(object)
    armed_signal = pyqtSignal()
    disarmed_signal = pyqtSignal()
    started_signal = pyqtSignal()
    stopped_signal = pyqtSignal()
    capture_mode_toggled_signal = pyqtSignal(object)

    def __init__(self, parent=None):
        super(CameraControlWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.arm_mode = ArmMode.DISARMED
        self.capture_mode = CaptureMode.CONTINUOUS
        self.trigger_source = TriggerSource.HARDWARE
        self.acquire_mode = AcquireMode.STOPPED

        self.arm_pushButton.clicked.connect(self.toggle_arm)
        self.start_pushButton.clicked.connect(self.toggle_start)

        self.capture_mode_buttonGroup.buttonClicked.connect(self.set_trigger_state)
        self.trigger_source_buttonGroup.buttonClicked.connect(self.set_trigger_state)

        self.exposure_time = round(float(self.exposure_lineEdit.text()), 2)
        self.exposure_lineEdit.editingFinished.connect(self.update_exposure)
        self.exposure_pushButton.clicked.connect(self.set_exposure)

        self.driver = None
        self.serial_number = ''
        self.imaging_systems = dict()
        self.populate_imaging_systems()
        self.imaging_system = None

    def populate_imaging_systems(self):
        for system in camerasettings.imaging_system_list:
            self.camera_comboBox.addItem(system.name)
            self.imaging_systems[system.name] = system

    def load_driver(self):
        if self.camera_comboBox.currentIndex() != 0:
            imaging_system_name = self.camera_comboBox.currentText()
            self.imaging_system = self.imaging_systems[imaging_system_name]
            self.serial_number = self.imaging_system.camera_serial_number
            self.driver = self.imaging_system.camera_type.driver
            try:
                self.software_trigger_pushButton.disconnect()
            except TypeError:
                pass
            try:
                self.driver.frame_captured_signal.disconnect()
            except TypeError:
                pass
            self.software_trigger_pushButton.clicked.connect(self.driver.execute_software_trigger)
            self.driver.frame_captured_signal.connect(self.frame_received_signal.emit)
        elif self.camera_comboBox.currentIndex() == 0:
            print('Please select imaging system!')
            self.driver = None
            self.serial_number = ''

    def arm(self):
        try:
            self.arm_pushButton.setText('Arming')
            QApplication.processEvents()
            self.load_driver()
            self.driver.arm_camera(self.serial_number)
            self.arm_mode = ArmMode.ARMED
            self.serial_label.setText(f'Serial Number: {self.serial_number}')
            self.arm_pushButton.setText('Disarm Camera')
            self.camera_comboBox.setEnabled(False)
            self.start_pushButton.setEnabled(True)
            self.exposure_pushButton.setEnabled(True)
            self.set_exposure()
            self.set_trigger_state()
            self.armed_signal.emit()
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
                self.arm_mode = ArmMode.DISARMED
                self.camera_comboBox.setEnabled(True)
                self.disarmed_signal.emit()
            except Exception as e:
                print('Error while trying to DISARM camera')
                print(e)
                self.abort()
        self.serial_label.setText(f'Serial Number: xxxxxxxx')
        self.arm_pushButton.setChecked(False)
        self.arm_pushButton.setText('Arm Camera')
        self.start_pushButton.setEnabled(False)
        self.exposure_pushButton.setEnabled(False)
        self.set_trigger_state()

    def toggle_arm(self):
        if self.arm_mode is ArmMode.DISARMED:
            self.arm()
        elif self.arm_mode is ArmMode.ARMED:
            self.disarm()

    def start(self):
        try:
            self.driver.start_acquisition()
            self.start_pushButton.setText('Stop Camera')
            self.acquire_mode = AcquireMode.STARTED
            self.set_trigger_state()
            if self.triggered_radioButton.isChecked() and self.software_trigger_radioButton.isChecked():
                self.software_trigger_pushButton.setEnabled(True)
            self.started_signal.emit()
        except Exception as e:
            print('Error while trying to START video')
            print(e)
            self.abort()

    def stop(self, aborting=False):
        if not aborting:
            try:
                self.driver.stop_acquisition()
            except Exception as e:
                print('Error while trying to STOP video')
                print(e)
                self.abort()
        self.start_pushButton.setText('Start Camera')
        self.acquire_mode = AcquireMode.STOPPED
        self.set_trigger_state()
        self.stopped_signal.emit()

    def toggle_start(self):
        if not self.driver.acquiring:
            self.start()
        else:
            self.stop()

    def set_trigger_state(self):
        if self.arm_mode is ArmMode.ARMED:
            if self.acquire_mode is AcquireMode.STOPPED:
                self.continuous_radioButton.setEnabled(True)
                self.triggered_radioButton.setEnabled(True)
                self.software_trigger_pushButton.setEnabled(False)
                if self.continuous_radioButton.isChecked():
                    self.capture_mode = CaptureMode.CONTINUOUS
                    self.software_trigger_radioButton.setEnabled(False)
                    self.hardware_trigger_radioButton.setEnabled(False)
                    self.driver.trigger_off()
                elif self.triggered_radioButton.isChecked():
                    self.capture_mode = CaptureMode.TRIGGERED
                    self.software_trigger_radioButton.setEnabled(True)
                    self.hardware_trigger_radioButton.setEnabled(True)
                    self.driver.trigger_on()
                    if self.hardware_trigger_radioButton.isChecked():
                        self.driver.set_hardware_trigger()
                    elif self.software_trigger_radioButton.isChecked():
                        self.driver.set_software_trigger()
                self.capture_mode_toggled_signal.emit(self.capture_mode)
            elif self.acquire_mode is AcquireMode.STARTED:
                if self.triggered_radioButton.isChecked() and self.software_trigger_radioButton.isChecked():
                    self.software_trigger_pushButton.setEnabled(True)
                self.continuous_radioButton.setEnabled(False)
                self.triggered_radioButton.setEnabled(False)
                self.software_trigger_radioButton.setEnabled(False)
                self.hardware_trigger_radioButton.setEnabled(False)
        if self.arm_mode is ArmMode.DISARMED:
            self.continuous_radioButton.setEnabled(False)
            self.triggered_radioButton.setEnabled(False)
            self.software_trigger_radioButton.setEnabled(False)
            self.hardware_trigger_radioButton.setEnabled(False)

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
        try:
            self.driver.close_connection()
        except AttributeError:
            pass
