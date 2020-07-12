import numpy as np
from enum import Enum,IntEnum

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

import AndorCamera as andor

class AcquisitionMonitor(QtCore.QThread):
	
	interface = None
	running = False
	
	def __init__(self, interface, parent=None):
		super(self.__class__, self).__init__(parent)
		self.interface = interface

	def __del__(self):
		if self.running:
			self.stop()
	
	def run(self):

		self.running = True
		
		self.interface.cam.start_acquisition()       
					
		try:
			#num = self.interface.cam.get_number_new_images()
			while self.running:
				if not self.interface.cam.wait_for_acquisition():
					# No new data
					if self.running:
						continue 
					else:
						break
				
				#~ first, last = self.interface.cam.get_number_new_images()
				#~ print(' # first {}, # last {}'.format(first, last))
				#~ first, last = self.interface.cam.get_number_available_images()
				#~ print(' # first {}, # last {}'.format(first, last))                
				#~ acc, series = self.interface.cam.get_series_progress()
				#~ print(' # acc {}, # ser {}'.format(acc, series))
				status = self.interface.cam.get_status()
				#~ print(' status {}'.format(status))
				
				if status == 'DRV_ACQUIRING':
					continue # Still capturing
				elif status == 'DRV_IDLE':
					pass # Capture frames complete
				else:
					raise Exception('Unexpected camera status ''{}'''.format(status))

				images = self.interface.get_acquisition()
				self.interface.captured_signal.emit(images)
				
				if self.running:
					self.interface.cam.start_acquisition()
		except Exception as e:
			print('Acquisition failed: {}'.format(e))
			self.running = False
			raise
		finally:
			print('Aborting acquisition')
			self.interface.cam.abort_acquisition()	
		
		#print('Leaving thread')	

	def stop(self):
		self.running = False
		
		if self.isRunning():
			print('Monitor thread is running. Trying to stop...')
			self.interface.cam.cancel_wait()
			if not self.wait(5000):
				print('Timedout waiting for thread to stop')

class Status(IntEnum):
	CLOSED = 0
	IDLE = 1
	ACQUIRING = 2
	
class AndorObject(QtCore.QObject):
	
	captured = QtCore.pyqtSignal(object)
	status_changed = QtCore.pyqtSignal(int)
	
	cameraId = None
	cam = None
	nFrames = 1
	mode = 0
	monitor = None
	
	def __init__(self, cameraId=None, parent=None):
		super(self.__class__, self).__init__(parent)
		self.cameraId = cameraId
		self._status = Status.CLOSED
	
	@property
	def status(self):
		return self._status
	
	@status.setter
	def status(self, value):
		self._status = value
		self.status_changed.emit(self._status)
	
	@QtCore.pyqtSlot()
	def open(self):
		if self.cameraId is not None:
			raise Exception('Opening camera by ID is not implemented')

		try:
			self.cam = andor.AndorCamera()
			self.status = Status.IDLE
		except Exception as e:
			if e.args[0] == 'DRV_VXNOTINSTALLED':
				print('Failed to open camera, is it in use?')
			else:
				print('Failed to open camera: ' + str(e))
			self.status = Status.CLOSED
		except:
			self.status = Status.CLOSED
			raise
	
	@QtCore.pyqtSlot()
	def close(self):
		if self.cam is None:
			return
			
		if self.status is Status.ACQUIRING:
			self.abort()
		
		self.cam.shut_down()
		self.cam = None

		self.status = Status.CLOSED

	@QtCore.pyqtSlot(object, int)
	def start_frames(self, config, nFrames=1, exposure=0.3, gain=1):
		if self.status is not Status.IDLE:
			raise Exception("Camera is not idle")
		
		try:
			self.mode = 1
			self.nFrames = nFrames
			
			self.cam.set_trigger_mode('External')
			self.cam.set_acquisition_mode('Kinetics')

			self.cam.set_image(*config.image_region)
			#self.cam.set_image(2, 2, 1, 1000, 1, 602)
			#self.cam.set_image(2, 2, 1, 1000, 215, 316)

			self.cam.set_hs_speed(0)
			self.cam.set_vs_speed(0)
			self.cam.set_preamp_gain(0)

			self.cam.set_exposure_time(config.exposure / 1000) # convert to sec
			self.cam.set_shutter(1,1)
			self.cam.set_number_kinetics(nFrames)
			self.cam.set_kinetic_cycle_time(0)
			self.cam.set_number_accumulations(1)        
			self.cam.set_accumulation_cycle_time(0)

			self.cam.get_acquisition_timings()

			print("Exposure time: {:.4f}".format(self.cam.info.exposure_time))
			print("Accumulate cycle time: {:.4f}".format(self.cam.info.accumulate_cycle_time))
			print("Kinetic cycle time: {:.4f}".format(self.cam.info.kinetic_cycle_time))

			self.monitor = AcquisitionMonitor(self)
			self.monitor.start()

			self.status = Status.ACQUIRING
		except:
			self.status = Status.IDLE
			raise

	@QtCore.pyqtSlot(object)
	def start_video(self, config, gain=1):
		if self.status is not Status.IDLE:
			raise Exception("Camera is not idle")
				
		try:
			self.mode = 2
			self.nFrames = 1

			self.cam.set_image(*config.image_region)
			
			#self.cam.set_image(2, 2, 1, 1000, 1, 1000)
			#cam.set_image(1, 1, 200, 703, 200, 703)
			self.cam.set_exposure_time(config.exposure / 1000) # convert to sec

			self.cam.set_shutter(1,1)

			self.cam.set_trigger_mode('Internal')
			self.cam.set_acquisition_mode('Run till abort')

			self.cam.get_acquisition_timings()

			print("Exposure time: {:.4f}".format(self.cam.info.exposure_time))
			#~ print("Accumulate cycle time: {:.4f}".format(self.cam.info.accumulate_cycle_time))
			print("Kinetic cycle time: {:.4f}".format(self.cam.info.kinetic_cycle_time))
			
			self.cam.start_acquisition()
			self.status = Status.ACQUIRING
		except:
			self.status = Status.IDLE
			raise

	@QtCore.pyqtSlot()
	def abort(self):
		if self.mode == 1:
			if self.monitor is not None:
				self.monitor.stop()
			self.monitor = None
		elif self.mode == 2:
			if self.cam is not None:
				self.cam.abort_acquisition()
			
		self.status = Status.IDLE
	
	def wait(self):
		#~ if not self.isOpen() or not self.acquiring:
			#~ raise Exception('Camera is not open')
		
		self.cam.wait_for_acquisition()

	def get_acquisition(self):
		#~ if not self.isOpen() or not self.acquiring:
			#~ raise Exception('Camera is not open')

		data = self.cam.get_acquired_data(self.nFrames)
		images = np.rot90(np.transpose(data, (2,1,0)), 2)
			
		return images

	def get_last_frame(self):
		#~ if not self.isOpen() or not self.acquiring:
			#~ raise Exception('Camera is not open')
		
		image = self.cam.get_most_recent_image()
		if image.size > 0:
			image = np.rot90(np.transpose(image), 2)
			
		return image
		
	def create_config_widget(self, parent):
		return AndorConfig(driver=self, parent=parent)

class AndorConfig(QWidget):
	
	def __init__(self, driver, parent=None):
		super(AndorConfig, self).__init__(parent)
		
		self.driver = driver
		
		self.driver.status_changed.connect(self.camera_status)
		
		self.setupUi()
		
	def camera_status(self, status):
		if status == Status.CLOSED:
			self.setEnabled(False)
		elif status == Status.IDLE: #  Camera enabled
			if self.driver.cam is None:
				return
			
			width = self.driver.cam.info.width
			height = self.driver.cam.info.height

			self.left.setMaximum(width)
			self.width.setMaximum(width - 1)
			self.top.setMaximum(height)
			self.height.setMaximum(height - 1)
			
			self.setEnabled(True)
		elif status == Status.ACQUIRING:
			self.setEnabled(False)
		else:
			pass #raise error?			


	def setupUi(self):

		layout = QFormLayout()	

		self.hbin = QSpinBox()
		self.hbin.setRange(1,1004)		
		self.hbin.setValue(2)
		self.hbin.valueChanged.connect(self.update_bin)

		self.vbin = QSpinBox()
		self.vbin.setRange(1,1002)
		self.vbin.setValue(2)
		self.vbin.valueChanged.connect(self.update_bin)
		
		self.left = QSpinBox()
		self.left.setRange(1,1004)
		self.left.setValue(1)		

		self.width = QSpinBox()
		self.width.setRange(1,1004)
		self.width.setSingleStep(2)
		self.width.setValue(1002)		

		self.top = QSpinBox()
		self.top.setRange(1,1002)		
		self.top.setValue(215)		

		self.height = QSpinBox()
		self.height.setRange(1,1002)
		self.height.setSingleStep(2)
		self.height.setValue(102)		

		self._exposure = QDoubleSpinBox()
		self._exposure.setMinimum(0.01)
		self._exposure.setMaximum(1000)
		self._exposure.setValue(0.3)		

		button_layout = QHBoxLayout()
		layout.addWidget(QLabel('Exposure:'))
		layout.addWidget(self._exposure)
		layout.addWidget(QLabel('Left:'))
		layout.addWidget(self.left)
		layout.addWidget(QLabel('Top: '))
		layout.addWidget(self.top)
		layout.addWidget(QLabel('Width:'))
		layout.addWidget(self.width)
		layout.addWidget(QLabel('Height:'))
		layout.addWidget(self.height)
		layout.addWidget(QLabel('H Bin:'))
		layout.addWidget(self.hbin)
		layout.addWidget(QLabel('V Bin:'))
		layout.addWidget(self.vbin)

		self.setLayout(layout)
		
		self.setMaximumWidth(80)
		
	def update_bin(self):
		hbin = self.hbin.value()
		vbin = self.vbin.value()
		
		width = self.width.value()
		width = (width // hbin) * hbin
		self.width.setValue(width)
		self.width.setSingleStep(hbin)
		
		height = self.height.value()
		height = (height // vbin) * vbin
		self.height.setValue(height)
		self.height.setSingleStep(vbin)
		
	@property
	def image_region(self):
		left = self.left.value()
		right = left + self.width.value() - 1
		top = self.top.value()
		bottom = top + self.height.value() - 1
		
		return (
			self.hbin.value(), self.vbin.value(),
			left, right, top, bottom
		)
	
	@property		
	def exposure(self):
		return self._exposure.value()
		
	@exposure.setter
	def exposure(self, val):
		self._exposure.setValue(val)
