import sys

try:
	from qtpy import QtCore
	from qtpy.QtWidgets import *
except:
	try:
		from PyQt5 import QtCore
		from PyQt5.QtWidgets import *
		QtCore.Signal = QtCore.pyqtSignal
	except:
		from PyQt4 import QtCore
		from PyQt4.QtGui import *
		QtCore.Signal = QtCore.pyqtSignal
		
import numpy as np
import pyqtgraph as pg

import AndorCamera as andor
from AndorDriver import AndorObject, AndorConfig, Status
from AnalysisWidgets import IntegrateROI
from colormaps import cmap

class AndorWindow(QMainWindow):
	
	cam = None
	
	def __init__(self, parent=None):
		super(AndorWindow, self).__init__(parent)

		self.worker = QtCore.QThread()
		self.cam = AndorObject()
		self.cam.moveToThread(self.worker)

		self.cam.status_changed.connect(self.onCameraStatus)
		
		self.worker.start()
		
		self.setupUi(self)

	def closeEvent(self, event):
		self.timer.stop()
		self.cam.abort()
		self.cam.close()
		
		self.worker.quit()

	def setupUi(self, Form):
		self.setWindowTitle("Andor Video")
		self.centralWidget = QWidget()
		self.setCentralWidget(self.centralWidget)
		self.resize(620,900)
		layout = QVBoxLayout()		

		self.config_widget = self.cam.create_config_widget(self)
		self.config_widget.setEnabled(False)

		self.camera_button = QPushButton('Start Camera')
		self.camera_button.setCheckable(True)
		self.camera_button.clicked.connect(self.toggleCamera)

		self.acquire_button = QPushButton('Start Acquisition')
		self.acquire_button.setCheckable(True)
		self.acquire_button.setEnabled(False)
		self.acquire_button.clicked.connect(self.toggleAcquire)
	
		self.im_widget = pg.ImageView(self)
		self.im_widget.ui.roiBtn.hide()
		self.im_widget.ui.menuBtn.hide()		
		self.im_histogram = self.im_widget.getHistogramWidget().item

		vLine = pg.InfiniteLine(angle=90, movable=True)
		hLine = pg.InfiniteLine(angle=0, movable=True)
		self.im_widget.addItem(vLine, ignoreBounds=True)
		self.im_widget.addItem(hLine, ignoreBounds=True)

		#self.im_widget.ui.histogram.hide()
		self.im_widget.setColorMap(cmap)
		
		self.history_widget = IntegrateROI(subtract_bkg=True, num_history=200)

		self.levels_button = QPushButton('Auto Scale', self)
		self.levels_button.clicked.connect(self.setLevels)       

		button_layout = QHBoxLayout()
		button_layout.addWidget(self.camera_button)
		button_layout.addWidget(self.acquire_button)
		button_layout.addWidget(self.levels_button)
		layout.addLayout(button_layout)

		#~ dock_widget = QDockWidget("Config", parent = self)
		#~ dock_widget.setWidget(self.config_widget)
		#~ dock_widget.setFeatures(QDockWidget.DockWidgetMovable)
		#~ dock_widget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
		#~ self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock_widget)

		layout2 = QHBoxLayout()
		layout2.addWidget(self.config_widget)
		layout2.addWidget(self.im_widget)
		layout.addLayout(layout2, stretch=2)

		#~ dock_widget = QDockWidget("History", parent = self)
		#~ dock_widget.setWidget(self.history_widget)
		#~ dock_widget.setFeatures(QDockWidget.DockWidgetMovable)
		#~ dock_widget.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
		#~ self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock_widget)
		
		layout.addWidget(self.history_widget, stretch=1)		

		self.centralWidget.setLayout(layout)       
		self.initFigure()
		self.initTimers()
		
	def toggleCamera(self):
		if self.camera_button.isChecked():
			self.camera_button.setText('Starting Camera...')
			QtCore.QMetaObject.invokeMethod(self.cam, 'open')
		else:
			self.camera_button.setText('Stopping Camera...')			
			QtCore.QMetaObject.invokeMethod(self.cam, 'close')
			
	def toggleAcquire(self):
		if self.acquire_button.isChecked():
			self.acquire_button.setText('Starting Acquisition...')
			QtCore.QMetaObject.invokeMethod(self.cam, 'start_video', QtCore.Q_ARG(object, self.config_widget))
		else:
			self.acquire_button.setText('Stopping Acquisition...')
			QtCore.QMetaObject.invokeMethod(self.cam, 'abort')

	def onCameraStatus(self, status):
		if status == Status.CLOSED:
			self.camera_button.setText('Start Camera')
			self.camera_button.setEnabled(True)
			self.camera_button.setChecked(False)
			self.acquire_button.setEnabled(False)
		elif status == Status.IDLE:
			self.camera_button.setText('Camera Open')
			self.camera_button.setEnabled(True)
			self.camera_button.setChecked(True)			
			self.acquire_button.setText('Start Acquisition')
			self.acquire_button.setEnabled(True)
			self.acquire_button.setChecked(False)			
		elif status == Status.ACQUIRING:
			self.acquire_button.setText('Acquisition Running')
			self.acquire_button.setEnabled(True)
			self.acquire_button.setChecked(True)
			self.camera_button.setEnabled(False)
		else:
			pass #raise error?
			
	def initTimers(self):
		self.timer = QtCore.QTimer(self)
		self.timer.timeout.connect(self.updateFigure)
		#self.cam.captured.connect(self.onCapture)
		self.timer.start(50)

	def initFigure(self):
		self.data = np.array([])
		self.history_widget.setup_figure(self.im_widget)
			   
	def setLevels(self):
		self.levels = (self.data.min(), self.data.max())
		self.im_widget.setLevels(min=self.levels[0], max=self.levels[1])
		self.im_histogram.setHistogramRange(self.levels[0], self.levels[1])

	def onCapture(self, image):
		self.data = image
		QtCore.QTimer.singleShot(0, self.processFigure)

	def updateFigure(self):
		if self.cam.status is not Status.ACQUIRING:
			return
		
		self.data = self.cam.get_last_frame()
		#QtCore.QTimer.singleShot(0, self.processFigure)
		if self.data.size > 0:
			self.processFigure()
		
	def processFigure(self):
		if self.data.size == 0:
			return
		
		self.im_widget.setImage(np.fliplr(self.data), autoLevels=False, autoHistogramRange=False)
		self.history_widget.analyze(self, self.im_widget.getImageItem())

## Start Qt event loop unless running in interactive mode.
def main():

	try:
		import ctypes
		myappid = u'ultracold.jkam' # arbitrary string
		ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)    
	except:
		pass
	
	app = QApplication(sys.argv)    
	app.setWindowIcon(QIcon('favicon.ico'))
	ex = AndorWindow()
	ex.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
