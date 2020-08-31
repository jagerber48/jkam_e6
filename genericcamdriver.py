import time
from PyQt5.QtCore import QObject, QThread, pyqtSignal


class FrameGrabber(QObject):
    captured = pyqtSignal(object)

    def __init__(self, driver, max_fps=50):
        super(FrameGrabber, self).__init__()
        self.driver = driver
        self.max_fps = max_fps
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.start()

    def grab_frames(self):
        while self.driver.acquiring:
            self.driver.grab_frame()
            time.sleep(1 / self.max_fps)  # Slow down frame rate to self.max_fps to give GUI time to update


class CameraDriver(QObject):
    frame_captured_signal = pyqtSignal(object)
    start_acquisition_signal = pyqtSignal()

    def __init__(self):
        super(CameraDriver, self).__init__()
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.start()

        self.frame_grabber = FrameGrabber(self)
        self.start_acquisition_signal.connect(self.frame_grabber.grab_frames)

        self._connect()
        self.cam_list = self._get_cam_list()
        self.cam = None
        self.serial_number = ''
        self.exposure_time = 0

        self.connected = False
        self.armed = False
        self.acquiring = False

    def _connect(self):
        """
        Create connection to camera interface system for camera device under control
        """
        raise NotImplementedError

    def _disconnect(self):
        """
        Close connection to camera interface system
        """
        raise NotImplementedError

    def _get_cam_list(self):
        """
        Return list of of accessible cameras
        """
        raise NotImplementedError

    @staticmethod
    def _get_cam_serial(cam):
        """
        Return serial number of cam as a string
        """
        raise NotImplementedError

    @staticmethod
    def _arm_camera(cam):
        """
        Establish communication with cam and initialize for acquisition
        """
        raise NotImplementedError

    @staticmethod
    def _disarm_camera(cam):
        """
        Disarm the camera to allow the program to access another camera or for shutdown.
        """
        raise NotImplementedError

    @staticmethod
    def _start_acquisition(cam):
        """
        Begin camera acquisition so that camera is ready to receive triggers and send frames
        """
        raise NotImplementedError

    @staticmethod
    def _stop_acquisition(cam):
        """
        End camera acquisition
        """
        raise NotImplementedError

    @staticmethod
    def _set_exposure_time(cam, exposure_time):
        """
        Set cam exposure time to exposure_time. exposure_time in ms
        """
        raise NotImplementedError

    @staticmethod
    def _trigger_on(cam):
        """
        enable hardware trigger
        """
        raise NotImplementedError

    @staticmethod
    def _trigger_off(cam):
        """
        disable hardware trigger
        """
        raise NotImplementedError

    @staticmethod
    def _grab_frame(cam):
        """
        Grab a single frame from cam. Return numpy array containing frame
        """
        raise NotImplementedError

    @staticmethod
    def _load_default_settings(cam):
        """
        Configure cam with default settings. This may include setting exposure time, setting gain to fixed value,
        disabling automatic exposure, gain, gamma or sharpness settings. It may also include configuring the camera
        to accept a hardware trigger with a rising edge and any other camera specific details.
        """
        raise NotImplementedError

    def find_camera(self, serial_number):
        print(f'Attempting to find camera device with serial number: {serial_number}')
        self.cam = None
        for camera in self.cam_list:
            cam_serial = self._get_cam_serial(camera)
            print(f'Found device with serial number: {cam_serial}')
            if cam_serial == serial_number:
                self.cam = camera
                self.serial_number = cam_serial
                print(f'SUCCESS set current camera with serial number: {self.serial_number}')
        if self.cam is None:
            print(f'FAILED to find camera with serial number: {serial_number}')

    def arm_camera(self, serial_number):
        """
        Establish communication with camera and initialize for acquisition
        """
        self.find_camera(serial_number)
        self._arm_camera(self.cam)
        self._load_default_settings(self.cam)
        self.armed = True
        print(f'ARMED Camera with serial number: {self.serial_number}')

    def disarm_camera(self):
        if self.acquiring:
            self.stop_acquisition()
        self._disarm_camera(self.cam)
        del self.cam
        self.cam = None
        self.armed = False
        print(f'DISARMED Camera with serial number: {self.serial_number}')
        self.serial_number = ''

    def start_acquisition(self):
        self._start_acquisition(self.cam)
        self.acquiring = True
        self.start_acquisition_signal.emit()
        print(f'STARTED camera with serial number: {self.serial_number}')

    def stop_acquisition(self):
        self._stop_acquisition(self.cam)
        self.acquiring = False
        print(f'STOPPED camera VIDEO with serial number: {self.serial_number}')

    def set_exposure_time(self, exposure_time):
        """
        Set camera exposure time to exposure_time. exposure_time express in ms
        """
        self.exposure_time = self._set_exposure_time(self.cam, exposure_time)
        print(f'EXPOSURE TIME set to {self.exposure_time:.4f} ms')

    def trigger_on(self):
        self._trigger_on(self.cam)
        print('Hardware trigger enabled')

    def trigger_off(self):
        self._trigger_off(self.cam)
        print('Hardware trigger disabled')

    def close_connection(self):
        if self.armed:
            self.disarm_camera()
        del self.cam
        self.cam = None
        self.cam_list.Clear()
        self._disconnect()
        self.connected = False
        print('Connection CLOSED')

    def grab_frame(self):
        frame = self._grab_frame(self.cam)
        if frame is not None:
            self.frame_captured_signal.emit(frame)
