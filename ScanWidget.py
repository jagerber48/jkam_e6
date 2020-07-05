import datetime
from shutil import copyfile, move
from os import makedirs, path

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
import h5py

class ScanWidget(QWidget):
	
	def __init__(self, camera_name, scan_root, log_root=None, save_csv=False, save_h5=True, parent=None):
		super(ScanWidget, self).__init__(parent)
		self.camera_name = camera_name
		self.scan_root = scan_root
		self.log_root = log_root
		self.save_csv = save_csv
		self.save_h5 = save_h5
		self.setupUi()
		
	def setupUi(self):
		
		today = datetime.date.today()
		self.scan_date = QLineEdit('{:%Y\\%b\\%d}'.format(today))
		self.scan_name = QLineEdit('scan1')
		
		self.scan_filenumber = QSpinBox()
		self.scan_filenumber.setMinimum(1)
		self.scan_filenumber.setMaximum(10000)
		self.scan_filenumber.setValue(1)
		
		self.scan_button = QPushButton('Start Scan')
		self.scan_button.setCheckable(True)
		
		scan_layout = QHBoxLayout()

		scan_layout.addWidget(QLabel('Data root:'))
		scan_layout.addWidget(QLabel(str(self.scan_root)))
		scan_layout.addWidget(QLabel('Date:'))
		scan_layout.addWidget(self.scan_date)
		scan_layout.addWidget(QLabel('Run name:'))
		scan_layout.addWidget(self.scan_name)
		scan_layout.addWidget(QLabel('_{}'.format(self.camera_name)))
		scan_layout.addWidget(QLabel('File number:'))
		scan_layout.addWidget(self.scan_filenumber)
		scan_layout.addWidget(self.scan_button)
		
		self.scan_button.clicked.connect(self.toggleScan)	
		
		self.setLayout(scan_layout)
		
	def isScanning(self):
		return self.scan_button.isChecked()
		
	def incrementScan(self):
		fileNumber = self.scan_filenumber.value()
		fileNumber = fileNumber + 1
		self.scan_filenumber.setValue(fileNumber)

	def toggleScan(self):
		if self.isScanning():
			
			filename, scanpath = self.getScanTarget()
			
			if not path.exists(scanpath):
				makedirs(scanpath)
			
			if path.exists(path.join(scanpath, filename+".txt")):
			
				msg = "The target file already exists, overwrite?"
				reply = QMessageBox.question(self, 'Overwrite confirmation', 
					 msg, QMessageBox.Yes, QMessageBox.No)

				if reply == QMessageBox.No:
					self.scan_button.setChecked(False)
					return

			self.scan_date.setEnabled(False)
			self.scan_name.setEnabled(False)
			self.scan_filenumber.setEnabled(False)
			self.scan_button.setText('Scan Running')

		else:
			self.scan_date.setEnabled(True)
			self.scan_name.setEnabled(True)
			self.scan_filenumber.setEnabled(True)
			
			today = datetime.date.today()
			self.scan_date.setText('{:%Y\\%b\\%d}'.format(today))
			
			self.scan_filenumber.setValue(1)
			
			self.scan_button.setText('Start Scan')        
		
	def getScanTarget(self):		
		scanDate = self.scan_date.text()
		scanName = self.scan_name.text()
		scanpath = path.join(self.scan_root, str(scanDate), '{}_{}'.format(str(scanName), self.camera_name))
	
		fileNumber = self.scan_filenumber.value()
		filename = 'image{:d}'.format(fileNumber)
		
		return filename, scanpath

	def getTimestampTarget(self, timestamp):
		targetdir = '{:%Y\\%m\\%d}'.format(timestamp)
		targetpath = path.join(self.log_root, targetdir)
		
		filename = '{:%Y-%m-%d-%H%M%S}'.format(timestamp)
		
		return filename, targetpath
		
	def saveData(self, capture, timestamp):
		if self.isScanning():
			filename, scanpath = self.getScanTarget()
			if not path.exists(scanpath):
				makedirs(scanpath)
			
			print('Output to {}.txt'.format(filename))
			
			fileStem = path.join(scanpath, filename)
			if self.save_csv:
				self._save_csv(fileStem, capture)
			if self.save_h5:
				self._save_h5(fileStem, capture, timestamp)
			
			self.incrementScan()
		elif self.log_root is not None:
			
			fileStem = path.join(self.log_root, self.camera_name)
			if self.save_csv:
				self._save_csv(fileStem, capture)
				print('Output to {}.txt'.format(self.camera_name))
			if self.save_h5:
				self._save_h5(fileStem, capture, timestamp)
				print('Output to {}.h5'.format(self.camera_name))
			
			filename, targetpath = self.getTimestampTarget(timestamp)
			if not path.exists(targetpath):
				makedirs(targetpath)
				
			try:
				targetStem = path.join(targetpath, filename)
				print('Copy to {}'.format(targetStem))
				if self.save_csv:
					for ext in (".txt","-sig.txt","-ref.txt","-bkg.txt"):
						copyfile(fileStem+ext, targetStem+ext)
				if self.save_h5:
					copyfile(fileStem+".h5", targetStem+".h5")
			except Exception as e:
				print('Error copying image:')
				print(e)						

		print('Output finished')

	def _save_csv(self, fileStem, capture):
		np.savetxt(fileStem+".txt", capture.data, delimiter=",", fmt='%.4f')
		np.savetxt(fileStem+"-sig.txt", capture.sig, delimiter=",", fmt='%d')
		np.savetxt(fileStem+"-ref.txt", capture.ref, delimiter=",", fmt='%d')
		np.savetxt(fileStem+"-bkg.txt", capture.bkg, delimiter=",", fmt='%d')
		
	def _save_h5(self, fileStem, capture, timestamp):
		with h5py.File(fileStem +".h5", 'w') as hf:
			#hf.create_dataset("abs",  data=capture.data.astype('float32')) #don't save normalized data in file, because it is redundant
			hf.create_dataset("sig",  data=capture.sig.astype('uint16'))
			hf.create_dataset("ref",  data=capture.ref.astype('uint16'))
			hf.create_dataset("bkg",  data=capture.bkg.astype('uint16'))
			hf.attrs['timestamp'] = timestamp.isoformat()		
