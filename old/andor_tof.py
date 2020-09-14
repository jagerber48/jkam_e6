import sys
from shutil import copyfile
from os import path
import datetime


from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
QtCore.Signal = QtCore.pyqtSignal

		
import numpy as np
import pyqtgraph as pg

from AndorDriver import AndorObject, Status
from AnalysisWidgets import AbsorptionROI
from old.ScanWidget import ScanWidget

# from colormaps import cmap

dataRoot = 'E:\\Data\\'
andorRoot = 'E:\\Andor\\'
webDest = 'W:\\internal\\e3\\andor.png'

class AndorWindow(QMainWindow):
	
	cam = None
	
	def __init__(self, parent=None):
		super(AndorWindow, self).__init__(parent)
		
		self.worker = QtCore.QThread()
		self.cam = AndorObject()
		self.cam.moveToThread(self.worker)

		self.cam.status_changed.connect(self.onCameraStatus)
		
		self.worker.start()
		
		self.setupUi()

	def closeEvent(self, event):
		self.cam.abort()
		self.cam.close()
		
		self.worker.quit()

	def setupUi(self):
		self.setWindowTitle("Andor TOF")
		self.centralWidget = QWidget()
		self.setCentralWidget(self.centralWidget)
		self.resize(1024,768)
		layout = QVBoxLayout()

		self.config_widget = self.cam.create_config_widget(self)
		self.config_widget.setEnabled(False)
	
		self.im_tof = pg.ImageView(self)
		self.im_sig = pg.ImageView(self)
		self.im_ref = pg.ImageView(self)
		self.im_bkg = pg.ImageView(self)
		
		for imView in (self.im_tof,self.im_sig,self.im_ref,self.im_bkg):
			imView.ui.roiBtn.hide()
			imView.ui.menuBtn.hide()
			# imView.setColorMap(cmap)
		
		self.im_tof.setLevels(.4, 1.1)
		self.im_histogram = self.im_tof.getHistogramWidget().item
		self.im_histogram.setHistogramRange(.4, 1.1)        

		self.im_stack = QTabWidget()
		self.im_stack.addTab(self.im_tof,"Normalized")
		self.im_stack.addTab(self.im_sig,"Signal")
		self.im_stack.addTab(self.im_ref,"Reference")
		self.im_stack.addTab(self.im_bkg,"Background") 
		self.im_stack.setTabPosition(QTabWidget.South)

		self.camera_button = QPushButton('Start Camera')
		self.camera_button.setCheckable(True)
		self.camera_button.clicked.connect(self.toggleCamera)
				
		self.acquire_button = QPushButton('Start Acquisition')
		self.acquire_button.setCheckable(True)
		self.acquire_button.setEnabled(False)
		self.acquire_button.clicked.connect(self.toggleAcquire)
				
		self.scan_widget = ScanWidget('andor', dataRoot, andorRoot, save_csv=False, save_h5=True, parent=self)
		self.history_widget = AbsorptionROI(cross_section=2.9e-9,pixel_size=2.86e-4, num_history=200, threshold=1000, parent=self)
		
		button_layout = QHBoxLayout()

		button_layout.addWidget(self.camera_button)
		button_layout.addWidget(self.acquire_button)
		layout.addLayout(button_layout)
		
		layout2 = QHBoxLayout()
		layout2.addWidget(self.config_widget)
		layout2.addWidget(self.im_stack)
		layout.addLayout(layout2)		
		
		layout.addWidget(self.scan_widget)
		layout.addWidget(self.history_widget)				
		self.centralWidget.setLayout(layout)       

		self.initFigure()
		self.cam.captured.connect(self.onCapture)

	def initFigure(self):
		self.data = np.array([])      
		self.history_widget.create_roi(self.im_tof)

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
			QtCore.QMetaObject.invokeMethod(self.cam, 'start_frames', QtCore.Q_ARG(object, self.config_widget), QtCore.Q_ARG(int, 3))
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
			   
	def setLevels(self):
		self.levels = (self.data.min(), self.data.max())
		self.im_tof.setLevels(min=self.levels[0], max=self.levels[1])
		self.im_histogram.setHistogramRange(self.levels[0], self.levels[1])

	def onCapture(self, images):
		self.sig = images[:,:,0]
		self.ref = images[:,:,1]
		self.bkg = images[:,:,2]
		
		with np.errstate(divide='ignore', invalid='ignore'):
			self.data = np.true_divide(self.sig - self.bkg, self.ref - self.bkg)

		self.timestamp = datetime.datetime.now()

		self.processFigure()

	def processFigure(self):
		if self.data.size == 0:
			return

		self.im_tof.setImage(np.fliplr(self.data), autoLevels=False, autoHistogramRange=False)
		self.im_sig.setImage(np.fliplr(self.sig))
		self.im_ref.setImage(np.fliplr(self.ref))
		self.im_bkg.setImage(np.fliplr(self.bkg))
		
		self.history_widget.analyze(self, self.im_tof.getImageItem())
		
		self.scan_widget.saveData(self, self.timestamp)
		self.saveFig()

	def saveFig(self):
		filename = "andor.png"
		image1 = path.join(andorRoot,filename)
		self.im_tof.getImageItem().save(image1)

		try:
			copyfile(image1, webDest)
		except Exception as e:
			print('Error copying image:')
			print(e)

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
