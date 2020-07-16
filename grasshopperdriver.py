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
                frame = np.transpose(frame)
                self.driver.captured_signal.emit(frame)
                image_result.Release()
                time.sleep(1/50)  # Slow down frame rate to 50 fps to give GUI time to update
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

        self.connected = False
        self.armed = False
        self.acquiring = False

    def find_camera(self, serial_number):
        print(f'Attempting to find camera device with serial number: {serial_number}')
        self.cam = None
        for camera in self.cam_list:
            cam_sn = camera.TLDevice.DeviceSerialNumber.GetValue()
            print(f'Found device with serial number: {cam_sn}')
            if cam_sn == serial_number:
                self.cam = camera
                self.serial_number = serial_number
                print(f'SUCCESS set current camera with serial number: {cam_sn}')
        if self.cam is None:
            print(f'FAILED to find camera with serial number: {serial_number}')

    def arm_camera(self, serial_number):
        self.find_camera(serial_number)
        self.cam.Init()
        self.load_default_settings()
        self.armed = True
        print(f'ARMED Camera with serial number: {serial_number}')

    def disarm_camera(self):
        if self.acquiring:
            self.cam.EndAcquisition()
            self.acquiring = False
        self.cam.DeInit()
        del self.cam
        self.cam = None
        self.armed = False
        print(f'DISARMED Camera with serial number: {self.serial_number}')

    def start_acquisition(self):
        # self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        self.cam.BeginAcquisition()
        self.acquiring = True
        self.start_video_signal.emit()
        print(f'STARTED camera VIDEO with serial number: {self.serial_number}')

    def stop_acquisition(self):
        self.cam.EndAcquisition()
        self.acquiring = False
        print(f'STOPPED camera VIDEO with serial number: {self.serial_number}')

    # def start_frames(self, n_frames=3):
    #     print(self.armed)
    #     if not self.armed:
    #         self.open_cam()
    #     self.cam.BeginAcquisition()
    #     self.acquiring = True
    #     frames = []
    #     for nFrame in range(n_frames):
    #         # input('Press enter for software trigger')
    #         # self.cam.TriggerSoftware.Execute()
    #         image_result = self.cam.GetNextImage(PySpin.EVENT_TIMEOUT_INFINITE)
    #         frames.append(image_result.GetNDArray())
    #         image_result.Release()
    #     self.cam.EndAcquisition()
    #     self.acquiring = False
    #     frames = np.stack(frames, axis=-1)
    #     self.captured_signal.emit(frames)

    def set_exposure_time(self, exposure_time):
        """
        exposure_time parameter is exposure time in ms. Grasshopper spinnaker/GENICAM API uses
        exposure times in us.
        """
        converted_exposure_time = exposure_time * 1e3
        self.cam.ExposureTime.SetValue(converted_exposure_time)
        exposure_time_result = self.cam.ExposureTime.GetValue() * 1e-3
        print(f'EXPOSURE TIME set to {exposure_time_result:.4f} ms')

    def trigger_on(self):
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)

    def trigger_off(self):
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)

    def close_connection(self):
        if self.armed:
            self.disarm_camera()
        del self.cam
        self.cam = None
        self.cam_list.Clear()
        self.system.ReleaseInstance()
        self.connected = False
        print('Connection CLOSED')

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
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
        self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
