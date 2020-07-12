import sys
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
from colormaps import cmap_dict
from GrasshopperDriver import GrasshopperDriver
from camerawindow_ui import Ui_CameraWindow


class CameraWindow(QtWidgets.QMainWindow, Ui_CameraWindow):
    grasshopper_sn = '17491535'

    def __init__(self):
        super(CameraWindow, self).__init__()
        self.driver = GrasshopperDriver()
        self.data = None
        self.levels = (0, 1)

        self.armed = False
        self.started = False

        self.setupUi(self)
        self.arm_pushButton.clicked.connect(self.toggle_arm)
        self.start_pushButton.clicked.connect(self.toggle_start)
        self.exposure_lineEdit.editingFinished.connect(self.update_exposure)
        self.exposure_pushButton.clicked.connect(self.set_exposure)
        self.autoscale_pushButton.clicked.connect(self.set_autoscale)
        self.fullscale_pushButton.clicked.connect(self.set_fullscale)
        self.customscale_pushButton.clicked.connect(self.set_customscale)
        self.cmap_comboBox.activated.connect(self.set_cmap)

        self.imageview_widget.ui.roiBtn.hide()
        self.imageview_widget.ui.menuBtn.hide()
        self.im_histogram = self.imageview_widget.getHistogramWidget().item
        self.im_histogram.setHistogramRange(0, 255)
        self.im_histogram.setLevels(0, 255)

        vLine = pg.InfiniteLine(angle=90, movable=True)
        hLine = pg.InfiniteLine(angle=0, movable=True)
        self.imageview_widget.addItem(vLine, ignoreBounds=True)
        self.imageview_widget.addItem(hLine, ignoreBounds=True)

        self.init_figure()
        self.driver.captured_signal.connect(self.on_capture)
        self.exposure_time = round(float(self.exposure_lineEdit.text()), 2)

    def abort(self):
        self.stop(aborting=True)
        self.disarm(aborting=True)

    def arm(self):
        serial_number = self.grasshopper_sn
        try:
            self.driver.arm_camera(serial_number)
            self.serial_label.setText(f'Serial Number: {serial_number}')
            self.arm_pushButton.setChecked(True)
            self.arm_pushButton.setText('Disarm Camera')
            self.start_pushButton.setEnabled(True)
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

    def init_figure(self):
        self.data = np.array([])
        self.history_widget.setup_figure(self.imageview_widget)

    def read_levels(self):
        try:
            level_min = float(self.min_lineEdit.text())
            level_max = float(self.max_lineEdit.text())
            self.levels = (level_min, level_max)
            return self.levels
        except ValueError:
            print('Invalid input for custom scale')
            self.write_levels()

    def write_levels(self):
        self.min_lineEdit.setText(f'{self.levels[0]:.2f}')
        self.max_lineEdit.setText(f'{self.levels[1]:.2f}')

    def set_customscale(self):
        self.read_levels()
        self.imageview_widget.setLevels(min=self.levels[0], max=self.levels[1])

    def set_autoscale(self):
        self.levels = (self.data.min(), self.data.max())
        self.imageview_widget.setLevels(min=self.levels[0], max=self.levels[1])
        self.write_levels()

    def set_fullscale(self):
        self.levels = (0, 255)
        self.imageview_widget.setLevels(min=self.levels[0], max=self.levels[1])
        self.im_histogram.setHistogramRange(self.levels[0], self.levels[1])
        self.write_levels()

    def set_cmap(self):
        cmap_name = self.cmap_comboBox.currentText().lower()
        cmap = cmap_dict[cmap_name]
        self.imageview_widget.setColorMap(cmap)
        self.im_histogram.gradient.showTicks(False)

    def on_capture(self, image):
        if self.driver.acquiring:
            self.data = image
            self.imageview_widget.setImage(np.transpose(image), autoRange=False,
                                           autoLevels=False, autoHistogramRange=False)
            self.imageview_widget.show()

    def closeEvent(self, event):
        self.driver.close_connection()


# Start Qt event loop unless running in interactive mode.
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QIcon('favicon.ico'))
    ex = CameraWindow()
    ex.show()
    app.exec_()


if __name__ == '__main__':
    main()
    sys.exit()
