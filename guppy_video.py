import sys
import time

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread

QtCore.Signal = QtCore.pyqtSignal

# try:
# 	from qtpy import QtCore
# 	from qtpy.QtWidgets import *
# 	from qtpy.QtGui import QIcon
# except:
# 	try:
# 		from PyQt5 import QtCore
# 		from PyQt5.QtWidgets import *
# 		from PyQt5.QtGui import QIcon
# 		QtCore.Signal = QtCore.pyqtSignal
# 	except:
# 		from PyQt4 import QtCore
# 		from PyQt4.QtGui import *
# 		QtCore.Signal = QtCore.pyqtSignal

import numpy as np
import pyqtgraph as pg

from false2 import cmap

# from GuppyDriver import GuppyObject
from GrasshopperDriver import GrasshopperObject
from AnalysisWidgets import IntegrateROI

class GuppyWindow(QMainWindow):
	video_signal = QtCore.pyqtSignal()

	def __init__(self, parent=None):
		super(GuppyWindow, self).__init__(parent)
		self.thread = QThread()
		self.moveToThread(self.thread)
		self.thread.start()
		
		self.cam = GrasshopperObject()
		self.video_signal.connect(self.cam.start_video)
		self.setupUi(self)

	def closeEvent(self, event):
		self.cam.abort()
		self.cam.close()

	def setupUi(self, Form):
		self.setWindowTitle("Guppy Video")
		self.centralWidget = QWidget()
		self.setCentralWidget(self.centralWidget)
		self.resize(620,1000)
		layout = QVBoxLayout()		

		self.camera_button = QPushButton('Start Camera')
		self.camera_button.setCheckable(True)
		self.camera_button.clicked.connect(self.toggleCamera)    
	
		self.im_widget = pg.ImageView(self)
		self.im_widget.ui.roiBtn.hide()
		self.im_widget.ui.menuBtn.hide()
		self.im_histogram = self.im_widget.getHistogramWidget().item

		vLine = pg.InfiniteLine(angle=90, movable=True)
		hLine = pg.InfiniteLine(angle=0, movable=True)
		self.im_widget.addItem(vLine, ignoreBounds=True)
		self.im_widget.addItem(hLine, ignoreBounds=True)

		# self.im_widget.ui.histogram.hide()
		self.im_widget.setColorMap(cmap)
		
		self.history_widget = IntegrateROI(subtract_bkg=True, num_history=200)
		
		self.levels_button = QPushButton('Auto Scale', self)
		self.levels_button.clicked.connect(self.setLevels)       

		layout.addWidget(self.camera_button)
		layout.addWidget(self.levels_button)
		layout.addWidget(self.im_widget, stretch=2)
		layout.addWidget(self.history_widget, stretch=1)
		self.centralWidget.setLayout(layout)

		self.initFigure()
		self.cam.captured.connect(self.onCapture)
		
	def toggleCamera(self):
		if self.camera_button.isChecked():
			try:
				self.cam.init_video()
				time.sleep(1)
				self.video_signal.emit()
				self.camera_button.setText('Camera Running')
			except:
				self.cam.abort()
				self.cam.close()
				self.camera_button.setChecked(False)
				raise
		else:
			self.cam.abort()
			self.cam.close()
			self.camera_button.setText('Start Camera')

	def initFigure(self):
		self.data = np.array([])
		self.history_widget.setupFigure(self.im_widget)

	def setLevels(self):
		self.levels = (self.data.min(), self.data.max())
		self.im_widget.setLevels(min=self.levels[0], max=self.levels[1])
		self.im_histogram.setHistogramRange(self.levels[0], self.levels[1])

	def onCapture(self, image):
		# print('received')
		self.processing = True
		self.im_widget.setImage(1.0*image, autoLevels=False, autoHistogramRange=False)
		self.processing = False
		self.video_signal.emit()

	# self.data = image  # [:,:,0]
		# self.processFigure()

	def processFigure(self):
		if self.data.size == 0:
			return
		# print(self.data)
		print('processed')
		# self.history_widget.analyze(self, self.im_widget.getImageItem())


## Start Qt event loop unless running in interactive mode.
def main():

	try:
		import ctypes
		myappid = u'ultracold.jkam' # arbitrary string
		ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)    
	except:
		pass

	result = 0
	app = QApplication(sys.argv)    
	app.setWindowIcon(QIcon('favicon.ico'))
	ex = GuppyWindow()
	ex.show()
	result = app.exec_()
		
	return result

if __name__ == '__main__':
	result = main()
	sys.exit(result)
