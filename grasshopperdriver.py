import numpy as np
import PySpin
from jkamgendriver import JKamGenDriver


class GrasshopperDriver(JKamGenDriver):
    def _open_connection(self):
        self.system = PySpin.System.GetInstance()

    def _close_connection(self):
        self.cam_list.Clear()
        self.system.ReleaseInstance()

    def _get_cam_list(self):
        self.cam_list = self.system.GetCameras()
        return self.cam_list

    @staticmethod
    def _get_cam_serial(cam):
        cam_serial = cam.TLDevice.DeviceSerialNumber.GetValue()
        return cam_serial

    @staticmethod
    def _arm_camera(cam):
        cam.Init()

    @staticmethod
    def _disarm_camera(cam):
        cam.DeInit()

    @staticmethod
    def _start_acquisition(cam):
        cam.BeginAcquisition()

    @staticmethod
    def _stop_acquisition(cam):
        cam.EndAcquisition()

    @staticmethod
    def _set_exposure_time(cam, exposure_time):
        """
        exposure time input in ms. Grasshopper spinnaker/GENICAM API uses exposure time in us
        Return actual exposure time in ms
        """
        converted_exposure_time = exposure_time * 1e3
        cam.ExposureTime.SetValue(converted_exposure_time)
        exposure_time_result = cam.ExposureTime.GetValue() * 1e-3
        return exposure_time_result

    @staticmethod
    def _trigger_on(cam):
        cam.TriggerMode.SetValue(PySpin.TriggerMode_On)

    @staticmethod
    def _trigger_off(cam):
        cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)

    @staticmethod
    def _grab_frame(cam):
        try:
            image_result = cam.GetNextImage(PySpin.EVENT_TIMEOUT_INFINITE)
            frame = image_result.GetNDArray()
            frame = np.transpose(frame)
            image_result.Release()
            return frame
        except PySpin.SpinnakerException:
            pass

    @staticmethod
    def _load_default_settings(cam):
        cam.UserSetSelector.SetValue(PySpin.UserSetSelector_Default)
        cam.UserSetLoad()

        cam.GainAuto.SetValue(PySpin.GainAuto_Off)
        cam.Gain.SetValue(0.0)

        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        cam.ExposureTime.SetValue(5000)

        PySpin.CBooleanPtr(cam.GetNodeMap().GetNode('GammaEnabled')).SetValue(False)

        PySpin.CBooleanPtr(cam.GetNodeMap().GetNode('SharpnessEnabled')).SetValue(False)

        frame_rate_node = PySpin.CEnumerationPtr(cam.GetNodeMap().GetNode('AcquisitionFrameRateAuto'))
        frame_rate_off = frame_rate_node.GetEntryByName('Off')
        frame_rate_node.SetIntValue(frame_rate_off.GetValue())
        PySpin.CBooleanPtr(cam.GetNodeMap().GetNode('AcquisitionFrameRateEnabled')).SetValue(True)
        cam.AcquisitionFrameRate.SetValue(25)

        s_node_map = cam.GetTLStreamNodeMap()
        handling_mode = PySpin.CEnumerationPtr(s_node_map.GetNode('StreamBufferHandlingMode'))
        handling_mode_NewestOnly = handling_mode.GetEntryByName('NewestOnly')
        handling_mode.SetIntValue(handling_mode_NewestOnly.GetValue())

        cam.TriggerActivation.SetValue(PySpin.TriggerActivation_RisingEdge)
        cam.TriggerSource.SetValue(PySpin.TriggerSelector_FrameStart)
        cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
        cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
        cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
