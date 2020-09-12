import time
from PyQt5.QtCore import QObject, QThread, pyqtSignal


class FrameGrabber(QObject):
    captured = pyqtSignal(object)

    def __init__(self, driver, max_fps=20):
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


class JKamGenDriver(QObject):
    """
    Generic driver with functionality to interface with jkam UI. Has a number of narrow-scope camera control
    methods which should be overridden in a custom driver for each type of camera to be implemented with jkam.
    """
    frame_captured_signal = pyqtSignal(object)
    start_acquisition_signal = pyqtSignal()

    def __init__(self):
        super(JKamGenDriver, self).__init__()
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.start()

        self.frame_grabber = FrameGrabber(self)
        self.start_acquisition_signal.connect(self.frame_grabber.grab_frames)

        self.open_connection()
        self.cam = None
        self.serial_number = ''
        self.exposure_time = 0

        self.connected = False
        self.armed = False
        self.acquiring = False

    def arm_camera(self, serial_number):
        """
        Establish communication with camera and initialize for acquisition
        """
        # self.find_camera(serial_number)
        self.cam = self._arm_camera(serial_number)
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
        print(f'STARTED camera acquisition with serial number: {self.serial_number}')

    def stop_acquisition(self):
        self._stop_acquisition(self.cam)
        self.acquiring = False
        print(f'STOPPED camera acquisition with serial number: {self.serial_number}')

    def set_exposure_time(self, exposure_time):
        """
        Set camera exposure time to exposure_time. exposure_time express in ms
        """
        self.exposure_time = self._set_exposure_time(self.cam, exposure_time)
        print(f'EXPOSURE TIME set to {self.exposure_time:.4f} ms')

    def trigger_on(self):
        self._trigger_on(self.cam)
        print('Trigger enabled')

    def trigger_off(self):
        self._trigger_off(self.cam)
        print('Trigger disabled')

    def set_software_trigger(self):
        self._set_software_trigger(self.cam)
        print('Software Trigger Enabled')

    def set_hardware_trigger(self):
        self._set_hardware_trigger(self.cam)
        print('Hardware Trigger Enabled')

    def execute_software_trigger(self):
        self._execute_software_trigger(self.cam)
        print('Software Trigger EXECUTED')

    def open_connection(self):
        self._open_connection()
        print('Connection OPENED')

    def close_connection(self):
        if self.armed:
            self.disarm_camera()
        del self.cam
        self.cam = None
        self._close_connection()
        self.connected = False
        print('Connection CLOSED')

    def grab_frame(self):
        frame = self._grab_frame(self.cam)
        if frame is not None:
            self.frame_captured_signal.emit(frame)

    def _open_connection(self):
        """
        Create connection to camera interface system for camera device under control
        """
        raise NotImplementedError

    def _close_connection(self):
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
    def _set_hardware_trigger(cam):
        """
        Configure camera to accept hardware trigger
        """
        raise NotImplementedError

    @staticmethod
    def _set_software_trigger(cam):
        """
        Configure camera to accept software trigger
        """
        raise NotImplementedError

    @staticmethod
    def _execute_software_trigger(cam):
        """
        Configure camera to accept software trigger
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
