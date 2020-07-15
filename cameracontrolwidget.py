from PyQt5.QtWidgets import QWidget
from cameracontrolwidget_ui import Ui_CameraControlWidget
from grasshopperdriver import GrasshopperDriver


class CameraControlWidget(QWidget, Ui_CameraControlWidget):
    grasshopper_sn = '17491535'

    def __init__(self, parent=None):
        super(CameraControlWidget, self).__init__(parent=parent)
        self.setupUi(self)
        self.driver = GrasshopperDriver()

        self.armed = False
        self.started = False
        self.exposure_time = round(float(self.exposure_lineEdit.text()), 2)

        self.arm_pushButton.clicked.connect(self.toggle_arm)
        self.start_pushButton.clicked.connect(self.toggle_start)
        self.exposure_lineEdit.editingFinished.connect(self.update_exposure)
        self.exposure_pushButton.clicked.connect(self.set_exposure)

    def arm(self):
        serial_number = self.grasshopper_sn
        try:
            self.driver.arm_camera(serial_number)
            self.serial_label.setText(f'Serial Number: {serial_number}')
            self.arm_pushButton.setChecked(True)
            self.arm_pushButton.setText('Disarm Camera')
            self.start_pushButton.setEnabled(True)
            self.set_exposure()
            self.armed = True
        except Exception as e:
            print('Error while trying to ARM camera')
            print(e)
            self.abort()

    def disarm(self, aborting=False):
        if not aborting:
            try:
                self.driver.disarm_camera()
            except Exception as e:
                print('Error while trying to DISARM camera')
                print(e)
                self.abort()
        self.serial_label.setText(f'Serial Number: xxxxxxxx')
        self.arm_pushButton.setChecked(False)
        self.arm_pushButton.setText('Arm Camera')
        self.start_pushButton.setEnabled(False)
        self.armed = False

    def toggle_arm(self):
        if not self.armed:
            self.arm()
        else:
            if self.started:
                self.stop()
            self.disarm()

    def start(self):
        try:
            self.driver.start_video()
            self.start_pushButton.setText('Stop Camera')
            self.video_radioButton.setEnabled(False)
            self.absorption_radioButton.setEnabled(False)
            self.started = True
        except Exception as e:
            print('Error while trying to START video')
            print(e)
            self.abort()

    def stop(self, aborting=False):
        if not aborting:
            try:
                self.driver.stop_video()
            except Exception as e:
                print('Error while trying to STOP video')
                print(e)
                self.abort()
        self.start_pushButton.setText('Start Camera')
        self.video_radioButton.setEnabled(True)
        self.absorption_radioButton.setEnabled(True)
        self.started = False

    def toggle_start(self):
        if not self.started:
            self.start()
        else:
            self.stop()

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
