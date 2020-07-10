import PySpin
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import time
import numpy as np


class FrameGrabber(QObject):
    captured = pyqtSignal(object)

    def __init__(self, driver):
        super(FrameGrabber, self).__init__()
        self.driver = driver
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.start()

    def get_frame(self):
        while self.driver.video_on:
            self.driver.cam.TriggerSoftware.Execute()
            image_result = self.driver.cam.GetNextImage(1000)  # PySpin.EVENT_TIMEOUT_INFINITE)
            frame = image_result.GetNDArray()
            time.sleep(0.050)
            self.driver.captured.emit(frame)
            image_result.Release()


class GrasshopperDriver(QObject):
    captured = pyqtSignal(object)
    start_video = pyqtSignal()

    def __init__(self):
        super(GrasshopperDriver, self).__init__()
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.start()
        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()

        self.frame_grabber = FrameGrabber(self)
        self.start_video.connect(self.frame_grabber.get_frame)
        self.video_on = False
        self.cam = None
        self.open = False
        self.open_cam()
        print('inited')

    def find_camera(self, serial_number):
        self.cam_list = self.system.GetCameras()
        print(f'Searching for device with serial number: {serial_number}')
        for camera in self.cam_list:
            new_device_serial = camera.TLDevice.DeviceSerialNumber.GetValue()
            print(f'Found device with serial number: {new_device_serial}')
            if new_device_serial == serial_number:
                self.cam = camera
                print(f'Set current camera with serial number: {new_device_serial}')

    def open_cam(self):
        ser_target = '18431942'
        self.find_camera(ser_target)
        self.cam.Init()
        # self.cam.UserSetSelector.SetValue(PySpin.UserSetSelector_Default)
        # self.cam.UserSetLoad()

        self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)
        self.cam.Gain.SetValue(0.0)
        self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        self.cam.ExposureTime.SetValue(1000)
        PySpin.CBooleanPtr(self.cam.GetNodeMap().GetNode('GammaEnabled')).SetValue(False)
        PySpin.CBooleanPtr(self.cam.GetNodeMap().GetNode('SharpnessEnabled')).SetValue(False)

        self.cam.TriggerActivation.SetValue(PySpin.TriggerActivation_RisingEdge)
        self.cam.TriggerSource.SetValue(PySpin.TriggerSelector_FrameStart)
        self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
        # self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Software)
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
        self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)

        self.open = True

    def init_video(self):
        if not self.open:
            self.open_cam()
        self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Software)
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
        self.cam.BeginAcquisition()
        self.video_on = True
        self.start_video.emit()

    def start_frames(self, n_frames=3):
        print(self.open)
        if not self.open:
            self.open_cam()
        self.cam.BeginAcquisition()
        frames = []
        for nFrame in range(n_frames):
            # input('Press enter for software trigger')
            # self.cam.TriggerSoftware.Execute()
            image_result = self.cam.GetNextImage(PySpin.EVENT_TIMEOUT_INFINITE)
            frames.append(image_result.GetNDArray())
            image_result.Release()
        self.cam.EndAcquisition()
        frames = np.stack(frames, axis=-1)
        self.captured.emit(frames)

    def close(self):
        print('closing')
        self.video_on = False
        self.open = False
        time.sleep(1)
        self.cam.EndAcquisition()
        self.cam.DeInit()
