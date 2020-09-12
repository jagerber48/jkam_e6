import numpy as np
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
        self.system.set_enum_string(cam, 'CycleMode', 'Fixed')

    def _trigger_off(self, cam):
        self.system.set_enum_string(cam, 'TriggerMode', 'Software')
        self.system.set_enum_string(cam, 'CycleMode', 'Continuous')

    def _set_hardware_trigger(self, cam):
        self.system.set_enum_string(cam, 'TriggerMode', 'External Start')

    def _set_software_trigger(self, cam):
        self.system.set_enum_string(cam, 'TriggerMode', 'Software')

    def _execute_software_trigger(self, cam):
        self.system.command(cam, 'SoftwareTrigger')

    def _grab_frame(self, cam):
        _, _ = self.system.wait_buffer(cam)

        np_arr = self.buf[0:self.config['aoiheight'] * self.config['aoistride']]
        np_d = np_arr.view(dtype='H')
        np_d = np_d.reshape(self.config['aoiheight'], round(np_d.size / self.config['aoiheight']))
        formatted_img = np_d[0:self.config['aoiheight'], 0:self.config['aoiwidth']]
        frame = formatted_img
        self.system.flush(cam)
        self.system.queue_buffer(cam, self.buf.ctypes.data, self.imageSizeBytes)

        return frame

    def _load_default_settings(self, cam):
        self.system.set_enum_string(cam, "PixelEncoding", "Mono16")

        self.imageSizeBytes = self.system.get_int(cam, "ImageSizeBytes")
        print("    Queuing Buffer (size", self.imageSizeBytes, ")")
        self.buf = np.empty((self.imageSizeBytes,), dtype='B')
        self.system.queue_buffer(cam, self.buf.ctypes.data, self.imageSizeBytes)

        self.config = {'aoiheight': self.system.get_int(cam, "AOIHeight"),
                       'aoiwidth': self.system.get_int(cam, "AOIWidth"),
                       'aoistride': self.system.get_int(cam, "AOIStride"),
                       'pixelencoding': self.system.get_enum_string(cam, "PixelEncoding")}
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
