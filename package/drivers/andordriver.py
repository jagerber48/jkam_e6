import numpy as np
import os
from package.drivers.andor_sdk.atcore import ATCore, ATCoreException
from package.drivers.jkamgendriver import JKamGenDriver

os.environ['PATH'] = os.path.dirname(__file__) + os.sep + 'andor_sdk' + ';' + os.environ['PATH']


class AndorDriver(JKamGenDriver):
    def _open_connection(self):
        self.sdk3 = ATCore()
        print('Connected to Andor driver')

    def _close_connection(self):
        pass

    def _get_serial_number(self, cam):
        return self.sdk3.get_string(cam, 'SerialNumber')

    def _arm_camera(self, serial_number):
        cam = self.sdk3.open(0)
        if self._get_serial_number(cam) == serial_number:
            return cam
        else:
            print(f'Andor camera with serial number: {serial_number} not found!')
            return None

    def _disarm_camera(self, cam):
        self.sdk3.flush(cam)
        self.sdk3.close(cam)

    def _start_acquisition(self, cam):
        self.sdk3.flush(cam)
        self.sdk3.command(cam, 'AcquisitionStart')

    def _stop_acquisition(self, cam):
        self.sdk3.command(cam, 'AcquisitionStop')
        self.sdk3.flush(cam)

    def _set_exposure_time(self, cam, exposure_time):
        """
        exposure time input in ms. Andor SDK3 sets exposure time in s and gets it in us.
        Return actual exposure time in ms
        """
        converted_exposure_time = exposure_time * 1e-3
        self.sdk3.set_float(cam, 'ExposureTime', converted_exposure_time)
        exposure_time_result = self.sdk3.get_float(cam, 'ExposureTime') * 1e3
        return exposure_time_result

    def _trigger_on(self, cam):
        pass

    def _trigger_off(self, cam):
        self._set_software_trigger(cam)

    def _set_hardware_trigger(self, cam):
        self.sdk3.set_enum_string(cam, 'TriggerMode', 'External')

    def _set_software_trigger(self, cam):
        self.sdk3.set_enum_string(cam, 'TriggerMode', 'Software')

    def _execute_software_trigger(self, cam):
        self.sdk3.command(cam, 'SoftwareTrigger')

    def _grab_frame(self, cam):
        self.sdk3.queue_buffer(cam, self.buf.ctypes.data, self.imageSizeBytes)
        if not self._trigger_enabled:
            self._execute_software_trigger(cam)
        try:
            _, _ = self.sdk3.wait_buffer(cam, timeout=ATCore.AT_INFINITE)
        except ATCoreException:
            return
        np_arr = self.buf[0:self.config['aoiheight'] * self.config['aoistride']]
        np_d = np_arr.view(dtype='H')
        np_d = np_d.reshape(self.config['aoiheight'], round(np_d.size / self.config['aoiheight']))
        formatted_img = np_d[0:self.config['aoiheight'], 0:self.config['aoiwidth']]
        frame = np.copy(formatted_img.astype(int))
        return frame

    def _load_default_settings(self, cam):
        self.sdk3.set_enum_string(cam, "SimplePreAmpGainControl", "12-bit (low noise)")
        self.sdk3.set_enum_string(cam, "PixelEncoding", "Mono12")
        # self.system.set_enum_string(cam, "SimplePreAmpGainControl", "16-bit (low noise & high well capacity)")
        # self.system.set_enum_string(cam, "PixelEncoding", "Mono16")
        self.sdk3.set_enum_string(cam, "AOIBinning", "8x8")
        self.sdk3.set_enum_string(cam, 'CycleMode', 'Continuous')

        self.imageSizeBytes = self.sdk3.get_int(cam, "ImageSizeBytes")
        print("    Queuing Buffer (size", self.imageSizeBytes, ")")
        self.buf = np.empty((self.imageSizeBytes,), dtype='B')

        self.config = {'aoiheight': self.sdk3.get_int(cam, "AOIHeight"),
                       'aoiwidth': self.sdk3.get_int(cam, "AOIWidth"),
                       'aoistride': self.sdk3.get_int(cam, "AOIStride"),
                       'pixelencoding': self.sdk3.get_enum_string(cam, "PixelEncoding")}
