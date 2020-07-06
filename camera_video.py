import sys
import time
import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread
import pyqtgraph as pg
from false2 import cmap
from GrasshopperDriver import GrasshopperObject
from AnalysisWidgets import IntegrateROI


class CameraWindow(QtWidgets.QMainWindow):
	video_signal = QtCore.pyqtSignal()

	def __init__(self):
		super(CameraWindow, self).__init__()
		self.thread = QThread()
		self.moveToThread(self.thread)
		self.thread.start()

		self.cam = GrasshopperObject()
		# self.video_signal.connect(self.cam.start_video)
		self.data = None
		self.levels = (0, 1)

		self.setWindowTitle("Guppy Video")
		self.centralWidget = QtWidgets.QWidget(self)
		self.setCentralWidget(self.centralWidget)
		self.resize(620, 1000)
		layout = QtWidgets.QVBoxLayout()

		self.camera_button = QtWidgets.QPushButton('Start Camera')
		self.camera_button.setCheckable(True)
		self.camera_button.clicked.connect(self.toggle_camera)
	
		self.im_widget = pg.ImageView(self)
		self.im_widget.ui.roiBtn.hide()
		self.im_widget.ui.menuBtn.hide()
		self.im_histogram = self.im_widget.getHistogramWidget().item
		self.im_histogram.setHistogramRange(0, 255)
		self.im_histogram.setLevels(0, 255)

		vLine = pg.InfiniteLine(angle=90, movable=True)
		hLine = pg.InfiniteLine(angle=0, movable=True)
		self.im_widget.addItem(vLine, ignoreBounds=True)
		self.im_widget.addItem(hLine, ignoreBounds=True)

		# self.im_widget.ui.histogram.hide()
		self.im_widget.setColorMap(cmap)
		
		self.history_widget = IntegrateROI(subtract_bkg=True, num_history=200)
		
		self.levels_button = QtWidgets.QPushButton('Auto Scale', self)
		# self.levels_button.clicked.connect(self.set_levels)

		layout.addWidget(self.camera_button)
		layout.addWidget(self.levels_button)
		layout.addWidget(self.im_widget, stretch=2)
		layout.addWidget(self.history_widget, stretch=1)
		self.centralWidget.setLayout(layout)

		self.init_figure()
		self.cam.captured.connect(self.on_capture)

	def closeEvent(self, event):
		self.cam.close()

	def toggle_camera(self):
		if self.camera_button.isChecked():
			try:
				self.cam.init_video()
				time.sleep(1)
				# self.video_signal.emit()
				self.camera_button.setText('Camera Running')
			except Exception:
				self.cam.close()
				self.camera_button.setChecked(False)
				raise
		else:
			self.cam.close()
			self.camera_button.setText('Start Camera')

	def init_figure(self):
		self.data = np.array([])
		self.history_widget.setup_figure(self.im_widget)

	def set_levels(self):
		self.levels = (self.data.min(), self.data.max())
		self.im_widget.setLevels(min=self.levels[0], max=self.levels[1])
		self.im_histogram.setHistogramRange(self.levels[0], self.levels[1])

	def on_capture(self, image):
		self.im_widget.setImage(image, autoRange=False, autoLevels=False, autoHistogramRange=False)
		self.video_signal.emit()


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
