import numpy as np

try:
	from qtpy import QtCore
except:
	try:
		from PyQt5 import QtCore
		QtCore.Signal = QtCore.pyqtSignal
	except:
		from PyQt4 import QtCore
		QtCore.Signal = QtCore.pyqtSignal

from pymba import Vimba

vimba = Vimba()
vimba.startup()

print('Vimba loaded, ver. {}'.format(vimba.version))

def shut_down():
	vimba.shutdown()
	print('Vimba unloaded')
	
import atexit
atexit.register(shut_down)

class GuppyObject(QtCore.QObject):
	
	captured = QtCore.Signal(object)
	
	cameraId = None
	cam = None
	frames = None

	def __init__(self, cameraId=None, parent=None):
		super(self.__class__, self).__init__(parent)       		
		self.cameraId = cameraId

	def open(self):
		if self.cameraId is None:
			cameraIds = vimba.camera_ids()
			cameraId = cameraIds[0]
		else:
			cameraId = self.cameraId

		# get and open a camera
		self.cam = vimba.camera(cameraId)
		self.cam.openCamera(1)
		
		self.cam.runFeatureCommand('AcquisitionStop') #Ensure acquisition is stopped, so we can write properties
		self.cam.TriggerMode = 'Off'
		self.cam.PixelFormat = 'Mono16'

	def isOpen(self):
		return not self.cam is None
		
	def close(self):
		if self.cam is None:
			return
		
		self.cam.closeCamera()
		self.cam = None

	def start_frames(self, exposure=5000, gain=24, nFrames=1):
		if self.cam is None:
			self.open()
		
		self.nFrames = nFrames
		
		self.cam.TriggerSelector = 'AcquisitionStart'
		self.cam.TriggerMode = 'On'

		self.cam.AcquisitionMode = 'Continuous'
		self.cam.ExposureMode = 'Timed'
		self.cam.ExposureTime = exposure #microseconds
		self.cam.Gain = gain
		self._start()
		
	def start_video(self, exposure=5000, gain=24):
		if self.cam is None:
			self.open()

		self.nFrames = 1

		self.cam.AcquisitionMode = 'Continuous'
		self.cam.TriggerMode = 'Off'
		self.cam.ExposureMode = 'Timed'
		self.cam.ExposureTime = exposure #microseconds
		self.cam.Gain = gain
		
		self._start()
		
	def _start(self):
	
		self.frames = [self.cam.getFrame() for idx in range(0, self.nFrames)]
		for frame in self.frames:
			frame.announceFrame()
		
		self.cam.startCapture()
		
		self._queue()
		self.cam.runFeatureCommand('AcquisitionStart')
						
	def isAcquiring(self):
		return not self.frames is None
		
	def abort(self):
		if self.frames is None:
			return
		
		self.cam.runFeatureCommand('AcquisitionStop')
		# clean up after capture
		self.cam.endCapture()
		self.cam.flushCaptureQueue()
		self.cam.revokeAllFrames()
		self.frames = None
	
	def _queue(self):    
		for frame in self.frames[0:-1]:
			frame.queueFrameCapture()

		self.frames[-1].queueFrameCapture(self._captured) #This callback is called from a thread started by the Vimba API
	
	def _captured(self, frame):
		images = self.get_acquisition()
		self._queue()
		self.captured.emit(images)
	
	def wait(self):
		self.frames[-1].waitFrameCapture()

	def get_acquisition(self):
			
		#~ frame = self.frames[idx]
		
		#~ buffer = frame.getBufferByteData()
		#~ image = np.ndarray(
			#~ shape=(frame.height, frame.width),
			#~ dtype=np.uint16, buffer=buffer)

		frame0 = self.frames[0]
		images = np.zeros(
			shape=(frame0.height, frame0.width, self.nFrames),
			dtype=np.uint16)
		
		for idx,frame in enumerate(self.frames):
			buffer = frame.getBufferByteData()
			images[:,:,idx] = np.ndarray(
				shape=(frame.height, frame.width),
				dtype=np.uint16, buffer=buffer)
			
		return images

	def get_last_frame(self, idx=0):
			
		frame = self.frames[idx]
		
		buffer = frame.getBufferByteData()
		image = np.ndarray(
			shape=(frame.height, frame.width),
			dtype=np.uint16, buffer=buffer)

		return image