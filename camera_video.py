import sys
import time
import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
from false2 import cmap
from GrasshopperDriver import GrasshopperDriver
from AnalysisWidgets import IntegrateROI
from camerawindow_ui import Ui_CameraWindow


class CameraWindow(QtWidgets.QMainWindow, Ui_CameraWindow):
	video_signal = QtCore.pyqtSignal()
	close_camera_signal = QtCore.pyqtSignal()
	grasshopper_sn = '17491535'

	def __init__(self):
		super(CameraWindow, self).__init__()
		self.cam_driver = GrasshopperDriver()
		self.close_camera_signal.connect(self.cam_driver.close_connection)
		# self.video_signal.connect(self.cam_driver.start_video)
		self.data = None
		self.levels = (0, 1)

		self.armed = False
		self.started = False

		self.setupUi(self)
		self.arm_pushButton.clicked.connect(self.toggle_arm)
		self.start_pushButton.clicked.connect(self.toggle_start)
		self.autoscale_pushButton.clicked.connect(self.set_levels)

		self.imageview_widget.ui.roiBtn.hide()
		self.imageview_widget.ui.menuBtn.hide()
		self.im_histogram = self.imageview_widget.getHistogramWidget().item
		self.im_histogram.setHistogramRange(0, 255)
		self.im_histogram.setLevels(0, 255)

		vLine = pg.InfiniteLine(angle=90, movable=True)
		hLine = pg.InfiniteLine(angle=0, movable=True)
		self.imageview_widget.addItem(vLine, ignoreBounds=True)
		self.imageview_widget.addItem(hLine, ignoreBounds=True)
		self.imageview_widget.setColorMap(cmap)

		self.init_figure()
		self.cam_driver.captured_signal.connect(self.on_capture)

	def arm(self):
		self.cam_driver.arm_camera(self.grasshopper_sn)
		self.arm_pushButton.setChecked(True)
		self.arm_pushButton.setText('Disarm Camera')
		self.start_pushButton.setEnabled(True)
		self.armed = True

	def disarm(self):
		self.cam_driver.disarm_camera()
		self.arm_pushButton.setChecked(False)
		self.arm_pushButton.setText('Arm Camera')
		self.start_pushButton.setEnabled(False)
		self.armed = False

	def toggle_arm(self):
		armed = not(self.arm_pushButton.isChecked())
		if not armed:
			self.arm()
		else:
			if self.started:
				self.stop()
			self.disarm()

	def start(self):
		self.cam_driver.start_video()
		self.start_pushButton.setText('Stop Camera')
		self.started = True

	def stop(self):
		self.cam_driver.stop_video()
		self.start_pushButton.setText('Start Camera')
		self.started = False

	def toggle_start(self):
		if not self.started:
			self.start()
		else:
			self.stop()

	def init_figure(self):
		self.data = np.array([])
		self.history_widget.setup_figure(self.imageview_widget)

	def set_levels(self):
		self.levels = (self.data.min(), self.data.max())
		self.imageview_widget.setLevels(min=self.levels[0], max=self.levels[1])
		self.im_histogram.setHistogramRange(self.levels[0], self.levels[1])

	def on_capture(self, image):
		if self.cam_driver.acquiring:
			self.imageview_widget.setImage(np.transpose(image), autoRange=False, autoLevels=False, autoHistogramRange=False)
			self.imageview_widget.show()

	def closeEvent(self, event):
		self.cam_driver.close_connection()

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
