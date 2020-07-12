import time
import numpy as np
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import PySpin


class FrameGrabber(QObject):
    captured = pyqtSignal(object)

    def __init__(self, driver):
        super(FrameGrabber, self).__init__()
        self.driver = driver
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.start()
        self.frame_num = 0

    def get_frame(self):
        while self.driver.acquiring:
            try:
                image_result = self.driver.cam.GetNextImage(PySpin.EVENT_TIMEOUT_INFINITE)
                frame = image_result.GetNDArray()
                self.driver.captured_signal.emit(frame)
                image_result.Release()
                time.sleep(1/30)  # Slow down frame rate to 30 fps to give GUI time to update
            except PySpin.SpinnakerException:
                pass


class GrasshopperDriver(QObject):
    captured_signal = pyqtSignal(object)
    start_video_signal = pyqtSignal()

    def __init__(self):
        super(GrasshopperDriver, self).__init__()
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.start()

        self.frame_grabber = FrameGrabber(self)
        self.start_video_signal.connect(self.frame_grabber.get_frame)

        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        self.cam = None
        self.serial_number = ''

        self.armed = False
        self.acquiring = False

    def find_camera(self, serial_number):
        self.cam = None
        for camera in self.cam_list:
            new_device_serial = camera.TLDevice.DeviceSerialNumber.GetValue()
            print(f'Found device with serial number: {new_device_serial}')
            if new_device_serial == serial_number:
                self.cam = camera
                self.serial_number = serial_number
                print(f'Set current camera with serial number: {new_device_serial}')

    def arm_camera(self, serial_number):
        print(f'Attempting to ARM camera with serial number: {serial_number}')
        self.find_camera(serial_number)
        try:
            self.cam.Init()
            self.load_default_settings()
            self.armed = True
            print(f'ARMED Camera with serial number: {serial_number}')
        except AttributeError as e:
            print(f'\nError while attempting to ARM camera with serial number: {serial_number}\n'
                  'Check connection with camera.')
            print(e)

    def disarm_camera(self):
        if self.acquiring:
            self.cam.EndAcquisition()
            self.acquiring = False
        self.cam.DeInit()
        del self.cam
        self.cam = None
        self.armed = False
        print(f'DISARMED Camera with serial number: {self.serial_number}')

    def start_video(self):
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        self.cam.BeginAcquisition()
        self.acquiring = True
        self.start_video_signal.emit()
        print(f'STARTED camera VIDEO with serial number: {self.serial_number}')

    def stop_video(self):
        self.cam.EndAcquisition()
        self.acquiring = False
        print(f'STOPPED camera VIDEO with serial number: {self.serial_number}')

    def start_frames(self, n_frames=3):
        print(self.armed)
        if not self.armed:
            self.open_cam()
        self.cam.BeginAcquisition()
        self.acquiring = True
        frames = []
        for nFrame in range(n_frames):
            # input('Press enter for software trigger')
            # self.cam.TriggerSoftware.Execute()
            image_result = self.cam.GetNextImage(PySpin.EVENT_TIMEOUT_INFINITE)
            frames.append(image_result.GetNDArray())
            image_result.Release()
        self.cam.EndAcquisition()
        self.acquiring = False
        frames = np.stack(frames, axis=-1)
        self.captured_signal.emit(frames)

    def close_connection(self):
        print('Closing connection')
        if self.armed:
            self.disarm_camera()
        del self.cam
        self.cam = None
        self.cam_list.Clear()
        self.system.ReleaseInstance()

    def load_default_settings(self):
        self.cam.UserSetSelector.SetValue(PySpin.UserSetSelector_Default)
        self.cam.UserSetLoad()

        self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)
        self.cam.Gain.SetValue(0.0)

        self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        self.cam.ExposureTime.SetValue(5000)

        PySpin.CBooleanPtr(self.cam.GetNodeMap().GetNode('GammaEnabled')).SetValue(False)

        PySpin.CBooleanPtr(self.cam.GetNodeMap().GetNode('SharpnessEnabled')).SetValue(False)

        frame_rate_node = PySpin.CEnumerationPtr(self.cam.GetNodeMap().GetNode('AcquisitionFrameRateAuto'))
        frame_rate_off = frame_rate_node.GetEntryByName('Off')
        frame_rate_node.SetIntValue(frame_rate_off.GetValue())
        PySpin.CBooleanPtr(self.cam.GetNodeMap().GetNode('AcquisitionFrameRateEnabled')).SetValue(True)
        self.cam.AcquisitionFrameRate.SetValue(25)

        s_node_map = self.cam.GetTLStreamNodeMap()
        handling_mode = PySpin.CEnumerationPtr(s_node_map.GetNode('StreamBufferHandlingMode'))
        handling_mode_NewestOnly = handling_mode.GetEntryByName('NewestOnly')
        handling_mode.SetIntValue(handling_mode_NewestOnly.GetValue())

        self.cam.TriggerActivation.SetValue(PySpin.TriggerActivation_RisingEdge)
        self.cam.TriggerSource.SetValue(PySpin.TriggerSelector_FrameStart)
        self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
        # self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Software)
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
        self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
