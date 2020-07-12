import time
import numpy as np
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
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
        while self.driver.video_on:
            # self.frame_num += 1
            # print(f'frame: {self.frame_num}')
            image_result = self.driver.cam.GetNextImage(PySpin.EVENT_TIMEOUT_INFINITE)  # PySpin.EVENT_TIMEOUT_INFINITE)
            frame = image_result.GetNDArray()
            self.driver.captured.emit(frame)
            # self.driver.window.im_widget.setImage(frame, autoRange=False,
            #                                       autoLevels=False, autoHistogramRange=False)
            # self.driver.window.on_capture(frame)
            image_result.Release()
            time.sleep(1/30)


class GrasshopperDriver(QObject):
    captured = pyqtSignal(object)
    start_video = pyqtSignal()

    def __init__(self, window):
        super(GrasshopperDriver, self).__init__()
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.start()
        # self.cam_list = self.system.GetCameras()
        self.window = window
        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        self.frame_grabber = FrameGrabber(self)
        self.start_video.connect(self.frame_grabber.get_frame)
        self.video_on = False
        self.cam = None
        self.armed = False
        self.acquiring = False
        self.open_cam()
        print('inited')

    def arm_camera(self, serial_number):
        print(f'Attempting connection with camera with serial number: {serial_number}')
        self.find_camera(serial_number)
        try:
            self.cam.Init()
            self.load_default_settings()
            self.armed = True
        except AttributeError:
            print('Error while attempting to arm camera with serial number {serial_number}\n'
                  'Check connection with camera.')

    def find_camera(self, serial_number):
        self.cam = None
        for camera in self.cam_list:
            new_device_serial = camera.TLDevice.DeviceSerialNumber.GetValue()
            print(f'Found device with serial number: {new_device_serial}')
            if new_device_serial == serial_number:
                self.cam = camera
                print(f'Set current camera with serial number: {new_device_serial}')

    def open_cam(self):
        # ser_target = '18431942'
        ser_target = '17491535'
        self.find_camera(ser_target)
        self.cam.Init()
        self.cam.UserSetSelector.SetValue(PySpin.UserSetSelector_Default)
        self.cam.UserSetLoad()

        self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)
        self.cam.Gain.SetValue(0.0)
        self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        self.cam.ExposureTime.SetValue(5000)
        PySpin.CBooleanPtr(self.cam.GetNodeMap().GetNode('GammaEnabled')).SetValue(False)
        PySpin.CBooleanPtr(self.cam.GetNodeMap().GetNode('SharpnessEnabled')).SetValue(False)
        node = PySpin.CEnumerationPtr(self.cam.GetNodeMap().GetNode('AcquisitionFrameRateAuto'))
        val = node.GetEntryByName('Off')
        node.SetIntValue(val.GetValue())
        # PySpin.CEnumerationPtr(self.cam.GetNodeMap().GetNode('AcquisitionFrameRateAuto')).SetValue('EnumEntry_AcquisitionFrameRateAuto_Off')
        PySpin.CBooleanPtr(self.cam.GetNodeMap().GetNode('AcquisitionFrameRateEnabled')).SetValue(True)
        self.cam.AcquisitionFrameRate.SetValue(25)

        s_node_map = self.cam.GetTLStreamNodeMap()
        handling_mode = PySpin.CEnumerationPtr(s_node_map.GetNode('StreamBufferHandlingMode'))
        handling_mode_entry = handling_mode.GetEntryByName('NewestOnly')
        handling_mode.SetIntValue(handling_mode_entry.GetValue())

        self.cam.TriggerActivation.SetValue(PySpin.TriggerActivation_RisingEdge)
        self.cam.TriggerSource.SetValue(PySpin.TriggerSelector_FrameStart)
        self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
        # self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Software)
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
        self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)

        self.armed = True

    def init_video(self):
        if not self.armed:
            self.open_cam()
        # self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Software)
        # self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        self.cam.BeginAcquisition()
        self.acquiring = True
        self.video_on = True
        self.start_video.emit()

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
        self.captured.emit(frames)

    def close(self):
        print('closing')
        self.video_on = False
        self.armed = False
        self.thread.sleep(2)
        print('cont')
        if self.acquiring:
            self.cam.EndAcquisition()
            self.acquiring = False
        self.cam.DeInit()
        del self.cam
        self.cam_list.Clear()
        self.system.ReleaseInstance()

    def load_default_settings(self):
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