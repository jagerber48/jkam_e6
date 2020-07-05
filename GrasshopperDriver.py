import sys
import PySpin
import matplotlib.pyplot as plt
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import time
import numpy as np
import datetime

system = PySpin.System.GetInstance()

class GrasshopperObject(QObject):
    captured = pyqtSignal(object)
    new_frame = pyqtSignal()

    def __init__(self):
        super(GrasshopperObject, self).__init__()
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.start()
        self.new_frame.connect(self.start_video)
        self.cam = None
        self.open = False
        self.open_cam()
        self.frame_num = 0
        print('inited')

    def open_cam(self):
        cam_list = system.GetCameras()
        try:
            self.cam = cam_list[0]
        except IndexError:
            'No Cameras Found'

        device_serial_number = self.cam.TLDevice.DeviceSerialNumber.GetValue()
        print('Device serial number retrieved as %s...' % device_serial_number)

        self.cam.Init()
        self.nodemap = self.cam.GetNodeMap()
        PySpin.CEnumerationPtr(self.nodemap.GetNode('GainAuto')).SetIntValue(PySpin.GainAuto_Off)
        PySpin.CEnumerationPtr(self.nodemap.GetNode('SharpnessAuto')).SetIntValue('EnumEntry_SharpnessAuto_Off')


        self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        self.cam.TriggerSource.SetValue(PySpin.TriggerSelector_FrameStart)
        # cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
        self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Software)
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
        self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)

        self.open = True

    def init_video(self):
        if not self.open:
            self.open_cam()
        # self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        self.cam.BeginAcquisition()

    def start_video(self):
        # print(f'{datetime.datetime.now().strftime("%H:%M:%S")} Acquiring images...')
        self.cam.TriggerSoftware.Execute()

        image_result = self.cam.GetNextImage(1000).GetNDArray()
        # frame = image_result
        # image_result.Release()
        # self.cam.EndAcquisition()
        # frames = np.stack(frames, axis=-1)
        self.captured.emit(image_result)
        self.frame_num += 1
        print(self.frame_num)
        # print('emitted')
        # time.sleep(0.02)

    def start_frames(self, nFrames=3):
        if not self.open:
            self.open_cam()
        self.cam.BeginAcquisition()
        frames = []
        # print('Acquiring images...')
        for nFrame in range(nFrames):
            # input('Press enter for software trigger')
            time.sleep(2)
            self.cam.TriggerSoftware.Execute()
            image_result = self.cam.GetNextImage(1000).GetNDArray()
            frames.append(image_result)
            # image_result.Release()
        self.cam.EndAcquisition()
        frames = np.stack(frames, axis=-1)
        self.captured.emit(frames)
        # self.start_frames(nFrames)

    def abort(self):
        pass

    def close(self):
        print('closing')
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        self.cam.DeInit()
        self.open = False


# if image_result.IsIncomplete():
#     print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
# else:
#     image_converted = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR).GetNDArray()
# plt.imshow(image_converted)
# image_result.Release()
# cam.EndAcquisition()
# cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
# cam.DeInit()

