import sys
from shutil import copyfile
from os import makedirs, path
import datetime

import numpy as np
import pyqtgraph as pg

try:
	from qtpy import QtCore
	from qtpy.QtWidgets import *
	from qtpy.QtGui import QIcon
except:
	try:
		from PyQt5 import QtCore
		from PyQt5.QtWidgets import *
		from PyQt5.QtGui import QIcon
		QtCore.Signal = QtCore.pyqtSignal
	except:
		from PyQt4 import QtCore
		from PyQt4.QtGui import *
		QtCore.Signal = QtCore.pyqtSignal

from GuppyDriver import GuppyObject
from AnalysisWidgets import AbsorptionROI
from ScanWidget import ScanWidget

from colormaps import cmap

dataRoot = 'E:\\Data\\'
andorRoot = 'E:\\Andor\\'

class GuppyWindow(QMainWindow):
	
	captured = QtCore.Signal()
	
	def __init__(self, parent=None):
		super(GuppyWindow, self).__init__(parent)
		
		self.cam = GuppyObject()
		
		self.setupUi()

	def closeEvent(self, event):
		self.cam.abort()
		self.cam.close()

	def setupUi(self):
		self.setWindowTitle("Guppy TOF")
		self.centralWidget = QWidget()
		self.setCentralWidget(self.centralWidget)
		self.resize(1024,768)
		layout = QVBoxLayout()		
	
		self.im_tof = pg.ImageView(self)
		self.im_sig = pg.ImageView(self)
		self.im_ref = pg.ImageView(self)
		self.im_bkg = pg.ImageView(self)
				
		for imView in (self.im_tof,self.im_sig,self.im_ref,self.im_bkg):
			imView.ui.roiBtn.hide()
			imView.ui.menuBtn.hide()
			imView.setColorMap(cmap)
			
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

		self.scan_widget = ScanWidget('guppy', dataRoot, andorRoot)
		self.history_widget = AbsorptionROI(cross_section=2.9e-9,pixel_size=1.46e-3, num_history=200)
		
		layout.addWidget(self.camera_button)
		layout.addWidget(self.im_stack)
		layout.addWidget(self.scan_widget)
		layout.addWidget(self.history_widget)				
		self.centralWidget.setLayout(layout)       

		self.initFigure()
		self.cam.captured.connect(self.onCapture)

	def initFigure(self):
		self.data = np.array([])
		self.history_widget.setup_figure(self.im_tof)

	def toggleCamera(self):
		if self.camera_button.isChecked():
			try:
				self.cam.start_frames(nFrames=3)
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
		#self.saveFig()

	def saveFig(self):
		filename = "guppy.png"
		image1 = path.join(andorRoot,filename)
		self.im_tof.getImageItem().save(image1)

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
