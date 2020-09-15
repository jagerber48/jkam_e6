import numpy as np
from atcore import ATCore, ATCoreException
from jkamgendriver import JKamGenDriver


class AndorDriver(JKamGenDriver):
    def _open_connection(self):
        self.system = ATCore()

    def _close_connection(self):
        pass

    def _arm_camera(self, serial_number):
        return self.system.open(0)

    def _disarm_camera(self, cam):
        self.system.flush(cam)
        self.system.close(cam)

    def _start_acquisition(self, cam):
        print('flushing')
        self.system.flush(cam)
        print('flushed')
        self.system.command(cam, 'AcquisitionStart')
        print('started')

    def _stop_acquisition(self, cam):
        print('stopping')
        self.system.command(cam, 'AcquisitionStop')
        print('stopped')

    def _set_exposure_time(self, cam, exposure_time):
        """
        exposure time input in ms. Andor SDK3 sets exposure time in s and gets it in us.
        Return actual exposure time in ms
        """
        converted_exposure_time = exposure_time * 1e-3
        self.system.set_float(cam, 'ExposureTime', converted_exposure_time)
        self.system.get_float(cam, 'ExposureTime')
        exposure_time_result = self.system.get_float(cam, 'ExposureTime') * 1e3
        return exposure_time_result

    def _trigger_on(self, cam):
        pass

    def _trigger_off(self, cam):
        self.system.set_enum_string(cam, 'TriggerMode', 'Software')

    def _set_hardware_trigger(self, cam):
        self.system.set_enum_string(cam, 'TriggerMode', 'External')

    def _set_software_trigger(self, cam):
        self.system.set_enum_string(cam, 'TriggerMode', 'Software')

    def _execute_software_trigger(self, cam):
        self.system.command(cam, 'SoftwareTrigger')

    def _grab_frame(self, cam):
        self.system.queue_buffer(cam, self.buf.ctypes.data, self.imageSizeBytes)
        if not self._trigger_enabled:
            self._execute_software_trigger(cam)
            print('triggered')
        try:
            _, _ = self.system.wait_buffer(cam, timeout=ATCore.AT_INFINITE)
        except ATCoreException:
            print('ATCoreException')
        np_arr = self.buf[0:self.config['aoiheight'] * self.config['aoistride']]
        np_d = np_arr.view(dtype='H')
        np_d = np_d.reshape(self.config['aoiheight'], round(np_d.size / self.config['aoiheight']))
        # formatted_img = np_d  # [0:self.config['aoiheight'], 0:self.config['aoiwidth']]
        frame = np_d
        return frame

    def _load_default_settings(self, cam):
        self.system.set_enum_string(cam, "SimplePreAmpGainControl", "12-bit (low noise)")
        self.system.set_enum_string(cam, 'CycleMode', 'Continuous')

        self.imageSizeBytes = self.system.get_int(cam, "ImageSizeBytes")
        print("    Queuing Buffer (size", self.imageSizeBytes, ")")
        self.buf = np.empty((self.imageSizeBytes,), dtype='B')
        # self.system.queue_buffer(cam, self.buf.ctypes.data, self.imageSizeBytes)

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
