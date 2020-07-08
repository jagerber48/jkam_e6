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
            image_result = self.driver.cam.GetNextImage(1000)
            frame = image_result.GetNDArray()
            time.sleep(0.050)
            self.driver.captured.emit(frame)
            image_result.Release()


class GrasshopperObject(QObject):
    captured = pyqtSignal(object)
    start_video = pyqtSignal()

    def __init__(self):
        super(GrasshopperObject, self).__init__()
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.start()
        self.system = PySpin.System.GetInstance()

        self.frame_grabber = FrameGrabber(self)
        self.start_video.connect(self.frame_grabber.get_frame)
        self.video_on = False
        self.cam = None
        self.open = False
        self.open_cam()
        print('inited')

    def open_cam(self):
        cam_list = self.system.GetCameras()
        try:
            self.cam = cam_list[1]
        except IndexError:
            print('No Cameras Found')
            return

        device_serial_number = self.cam.TLDevice.DeviceSerialNumber.GetValue()
        print('Device serial number retrieved as %s...' % device_serial_number)
        self.cam.Init()

        self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)
        self.cam.Gain.SetValue(0.0)
        self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        self.cam.ExposureTime.SetValue(20000)
        # self.cam.Gamma.SetValue(1.0)

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
        self.cam.BeginAcquisition()
        self.video_on = True
        self.start_video.emit()

    def start_frames(self, nFrames=3):
        if not self.open:
            self.open_cam()
        self.cam.BeginAcquisition()
        frames = []
        for nFrame in range(nFrames):
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
        time.sleep(0.25)
        self.cam.EndAcquisition()
        self.cam.DeInit()
        self.open = False
