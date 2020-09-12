from andor_sdk.atcore import ATCore
from jkamgendriver import JKamGenDriver


class AndorDriver(JKamGenDriver):
    def _open_connection(self):
        self.system = ATCore()

    def _close_connection(self):
        self.system.close(self.cam)

    def _arm_camera(self, serial_number):
        return self.system.open(0)

    @staticmethod
    def _disarm_camera(cam):
        pass

    def _start_acquisition(self, cam):
        self.system.command(cam, 'AcquisitionStart')

    def _stop_acquisition(self, cam):
        self.system.command(cam, 'AcquisitionStop')

    def _set_exposure_time(self, cam, exposure_time):
        """
        exposure time input in ms. Andor SDK3 uses exposure time in s
        Return actual exposure time in ms
        """
        converted_exposure_time = exposure_time * 1e-3
        self.system.set_float(cam, 'ExposureTime', converted_exposure_time)
        self.system.get_float(cam, 'ExposureTime')
        exposure_time_result = self.system.get_float(cam, 'ExposureTime') * 1e-3
        return exposure_time_result

    def _trigger_on(self, cam):
        self.system.set_enum_string(cam, 'TriggerMode', 'ExternalStart')

    def _trigger_off(self, cam):
        self.system.set_enum_string(cam, 'TriggerMode', 'Internal')

    def _set_hardware_trigger(self, cam):
        self._trigger_on(cam)

    def _set_software_trigger(self, cam):
        self._trigger_off(cam)

    def _execute_software_trigger(self, cam):
        self.system.command(cam, 'SoftwareTrigger')

    def _grab_frame(self, cam):
        image_result = self.system.wait_buffer(cam)
        frame = image_result
        return frame

    @staticmethod
    def _load_default_settings(cam):
        pass
        # cam.UserSetSelector.SetValue(PySpin.UserSetSelector_Default)
        # cam.UserSetLoad()
        #
        # cam.GainAuto.SetValue(PySpin.GainAuto_Off)
        # cam.Gain.SetValue(0.0)
        #
        # cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        # cam.ExposureTime.SetValue(5000)
        #
        # PySpin.CBooleanPtr(cam.GetNodeMap().GetNode('GammaEnabled')).SetValue(False)
        #
        # PySpin.CBooleanPtr(cam.GetNodeMap().GetNode('SharpnessEnabled')).SetValue(False)
        #
        # frame_rate_node = PySpin.CEnumerationPtr(cam.GetNodeMap().GetNode('AcquisitionFrameRateAuto'))
        # frame_rate_off = frame_rate_node.GetEntryByName('Off')
        # frame_rate_node.SetIntValue(frame_rate_off.GetValue())
        # PySpin.CBooleanPtr(cam.GetNodeMap().GetNode('AcquisitionFrameRateEnabled')).SetValue(True)
        # cam.AcquisitionFrameRate.SetValue(25)
        #
        # s_node_map = cam.GetTLStreamNodeMap()
        # handling_mode = PySpin.CEnumerationPtr(s_node_map.GetNode('StreamBufferHandlingMode'))
        # handling_mode_NewestOnly = handling_mode.GetEntryByName('NewestOnly')
        # handling_mode.SetIntValue(handling_mode_NewestOnly.GetValue())
        #
        # cam.TriggerActivation.SetValue(PySpin.TriggerActivation_RisingEdge)
        # cam.TriggerSource.SetValue(PySpin.TriggerSelector_FrameStart)
        # cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
        # cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
        # cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
