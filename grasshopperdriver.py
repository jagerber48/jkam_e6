import numpy as np
import PySpin
from jkamgendriver import JKamGenDriver


class GrasshopperDriver(JKamGenDriver):
    def _open_connection(self):
        self.system = PySpin.System.GetInstance()

    def _close_connection(self):
        self.system.ReleaseInstance()

    def _find_camera(self, serial_number):
        print(f'Attempting to find camera device with serial number: {serial_number}')
        cam_list = self.system.GetCameras()
        cam = None
        for camera in cam_list:
            cam_serial = camera.TLDevice.DeviceSerialNumber.GetValue()
            print(f'Found device with serial number: {cam_serial}')
            if cam_serial == serial_number:
                cam = camera
                print(f'SUCCESS set current camera with serial number: {serial_number}')
        if cam is None:
            print(f'FAILED to find camera with serial number: {serial_number}')
        return cam

    def _arm_camera(self, serial_number):
        cam = self._find_camera(serial_number)
        cam.Init()
        return cam

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
    def _set_hardware_trigger(cam):
        cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
        cam.TriggerMode.SetValue(PySpin.TriggerMode_On)

    @staticmethod
    def _set_software_trigger(cam):
        cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        cam.TriggerSource.SetValue(PySpin.TriggerSource_Software)
        cam.TriggerMode.SetValue(PySpin.TriggerMode_On)

    @staticmethod
    def _execute_software_trigger(cam):
        cam.TriggerSoftware.Execute()

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
