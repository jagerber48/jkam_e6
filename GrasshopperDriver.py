import PySpin
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import time
import numpy as np


class GrasshopperObject(QObject):
    captured = pyqtSignal(object)
    new_frame = pyqtSignal()

    def __init__(self):
        super(GrasshopperObject, self).__init__()
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.start()
        self.new_frame.connect(self.start_video)
        self.system = PySpin.System.GetInstance()

        self.cam = None
        self.open = False
        self.open_cam()
        self.frame_num = 0
        print('inited')

    def open_cam(self):
        cam_list = self.system.GetCameras()
        try:
            self.cam = cam_list[0]
        except IndexError:
            print('No Cameras Found')
            return

        device_serial_number = self.cam.TLDevice.DeviceSerialNumber.GetValue()
        print('Device serial number retrieved as %s...' % device_serial_number)

        self.cam.Init()

        self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)
        self.cam.Gain.SetValue(0.0)
        self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        self.cam.ExposureTime.SetValue(10000)
        self.cam.Gamma.SetValue(1.0)

        self.cam.TriggerSource.SetValue(PySpin.TriggerSelector_FrameStart)
        # cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
        self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Software)
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
        self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)

        self.open = True

    def init_video(self):
        if not self.open:
            self.open_cam()
        self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Software)
        self.cam.BeginAcquisition()

    def start_video(self):
        self.cam.TriggerSoftware.Execute()
        image_result = self.cam.GetNextImage(1000)
        frame = image_result.GetNDArray()
        self.captured.emit(frame)
        image_result.Release()
        time.sleep(0.050)

    def start_frames(self, nFrames=3):
        if not self.open:
            self.open_cam()
        self.cam.BeginAcquisition()
        frames = []
        for nFrame in range(nFrames):
            input('Press enter for software trigger')
            self.cam.TriggerSoftware.Execute()
            image_result = self.cam.GetNextImage(1000)
            frames.append(image_result.GetNDArray())
            image_result.Release()
        self.cam.EndAcquisition()
        frames = np.stack(frames, axis=-1)
        self.captured.emit(frames)

    def close(self):
        print('closing')
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        self.cam.DeInit()
        self.open = False
