import ctypes as c
from os import path
import platform

import numpy as np

from old.configuration import andor_configuration as config

if platform.system() == "Windows":
    library_loader = c.windll

    if platform.architecture()[0] == "32bit":
        library_path = "atmcd32d.dll"
        if not path.exists(library_path):
            library_path = "C:\\Program Files (x86)\\Andor SOLIS\\atmcd32d.dll"
        if not path.exists(library_path):
            library_path = "C:\\Program Files\\Andor iXon\\atmcd32d.dll"
        if not path.exists(library_path):
            library_path = "C:\\Program Files\\Andor iXon 4.9\\atmcd32d.dll"
    else:
        library_path = "atmcd64d.dll"
        if not path.exists(library_path):
            library_path = "C:\\Program Files\\Andor SOLIS\\Drivers\\atmcd64d.dll"
        if not path.exists(library_path):
            library_path = "C:\\Program Files\\Andor Driver Pack 2\\atmcd64d.dll"
        if not path.exists(library_path):
            library_path = "C:\\Program Files (x86)\\Andor SOLIS\\atmcd32d_sdk3.dll"

elif platform.system() == "Linux":
    library_path = "/usr/local/lib/libandor.so"
    library_loader = c.cdll
else:
    raise SystemError("Unsupported operating system")

if not path.exists(library_path):
    raise SystemError("Failed to locate Andor SDK")

dll = library_loader.LoadLibrary(library_path)

'''Adapted from https://code.google.com/p/pyandor/'''


class AndorInfo(object):

    def __init__(self):
        self.width = None
        self.height = None
        self.min_temp = None
        self.max_temp = None
        self.cooler_state = None
        self.temperature_setpoint = None
        self.temperature = None
        self.serial_number = None
        self.min_gain = None
        self.max_gain = None
        self.emccd_gain = None
        self.read_mode = None
        self.acquisition_mode = None
        self.trigger_mode = None
        self.exposure_time = None
        self.accumulate_cycle_time = None
        self.kinetic_cycle_time = None
        self.image_region = None
        self.number_kinetics = None
        self.number_accumulations = None


def get_available_cameras():
    num_cameras = c.c_long()
    error = dll.GetAvailableCameras(c.byref(num_cameras))
    if ERROR_CODE[error] != 'DRV_SUCCESS':
        raise Exception(ERROR_CODE[error])
    return num_cameras.value


class AndorCamera(object):
    """
	Andor class which is meant to provide the Python version of the same
	functions that are defined in the Andor's SDK. Since Python does not
	have pass by reference for immutable variables, some of these variables
	are actually stored in the class instance. For example the temperature,
	gain, gainRange, status etc. are stored in the class.
	"""

    handle = None

    def __init__(self, cameraId=None):

        if cameraId is not None:
            handle = c.c_long()
            error = dll.GetCameraHandle(cameraId, c.byref(handle))
            if ERROR_CODE[error] != 'DRV_SUCCESS':
                raise Exception(ERROR_CODE[error])
            self.handle = handle.value
            print(self.handle)

        self._select()

        print('Initializing Camera...')
        error = dll.Initialize(path.dirname(__file__))
        if ERROR_CODE[error] != 'DRV_SUCCESS':
            raise Exception(ERROR_CODE[error])
        print('Done Initializing')

        self.info = AndorInfo()
        self._get_detector_dimensions()
        self.get_temperature_range()
        self.acquire_camera_serial_number()
        self.get_camera_em_gain_range()
        self.get_emccd_gain()

        self.set_read_mode(config.read_mode)
        self.set_acquisition_mode(config.acquisition_mode)
        self.set_trigger_mode(config.trigger_mode)
        self.set_exposure_time(config.exposure_time)

        self.outamp = 0
        if config.output_amp is not None:
            self.set_output_amp(config.output_amp)
        if config.hs_speed is not None:
            self.set_hs_speed(config.hs_speed)
        if config.vs_speed is not None:
            self.set_vs_speed(config.vs_speed)
        if config.preamp_gain is not None:
            self.set_preamp_gain(config.preamp_gain)

        # set image to full size with the default binning
        (hbin, vbin, hstart, hend, vstart, vend) = config.image_region
        self.set_image(hbin, vbin, hstart, hend, vstart, vend)
        if config.cooler:
            print("Turning cooler on");
            self.set_cooler_on()
            self.set_temperature(config.set_temperature)
            self.get_cooler_state()
            self.get_temperature()
        else:
            print("Turning cooler off");
            self.set_cooler_off()
            self.get_cooler_state()

    def _select(self):
        if self.handle is not None:
            error = dll.SetCurrentCamera(c.c_long(self.handle))
            if ERROR_CODE[error] != 'DRV_SUCCESS':
                raise Exception(ERROR_CODE[error])

    def __del__(self):
        try:
            print('Shutting down camera')
            self.shut_down()
        except Exception as e:
            print('Error shutting down camera: ' + str(e))

    def get_software_version(self):
        '''
		gets the version of the SDK
		'''
        eprom = c.c_int()
        cofFile = c.c_int()
        vxdRev = c.c_int()
        vxdVer = c.c_int()
        dllRev = c.c_int()
        dllVer = c.c_int()
        error = dll.GetSoftwareVersion(c.byref(eprom), c.byref(cofFile), c.byref(vxdRev), c.byref(vxdVer),
                                       c.byref(dllRev), c.byref(dllVer))
        if ERROR_CODE[error] != 'DRV_SUCCESS':
            raise Exception(ERROR_CODE[error])

        return (eprom.value, cofFile.value, vxdRev.value, vxdVer.value, dllRev.value, dllVer.value)

    def print_software_version(self):
        (eprom, cofFile, vxdRev, vxdVer, dllRev, dllVer) = self.get_software_version()

        print('Software Version')
        print("EPROM version: {}".format(eprom))
        print("COF version: {}".format(cofFile))
        print("Driver version: {}.{}".format(vxdVer, vxdRev))
        print("Library version: {}.{}".format(dllVer, dllRev))

    def print_get_capabilities(self):
        '''
		gets the exact capabilities of the camera
		'''

        class AndorCapabilities(c.Structure):
            _fields_ = [('ulSize', c.c_ulong),
                        ('ulAcqModes', c.c_ulong),
                        ('ulReadModes', c.c_ulong),
                        ('ulTriggerModes', c.c_ulong),
                        ('ulCameraType', c.c_ulong),
                        ('ulPixelMode', c.c_ulong),
                        ('ulSetFunctions', c.c_ulong),
                        ('ulGetFunctions', c.c_ulong),
                        ('ulFeatures', c.c_ulong),
                        ('ulPCICard', c.c_ulong),
                        ('ulEMGainCapability', c.c_ulong),
                        ('ulFTReadModes', c.c_ulong),
                        ]

        caps = AndorCapabilities()
        caps.ulSize = c.c_ulong(c.sizeof(caps))
        error = dll.GetCapabilities(c.byref(caps))
        print('ulAcqModes', '{:07b}'.format(caps.ulAcqModes))
        print('ulReadModes', '{:06b}'.format(caps.ulReadModes))
        print('ulTriggerModes', '{:08b}'.format(caps.ulTriggerModes))
        print('ulCameraType', '{}'.format(caps.ulCameraType))
        print('ulPixelMode', '{:032b}'.format(caps.ulPixelMode))
        print('ulSetFunctions', '{:025b}'.format(caps.ulSetFunctions))
        print('ulGetFunctions', '{:016b}'.format(caps.ulGetFunctions))
        print('ulFeatures', '{:020b}'.format(caps.ulFeatures))
        print('ulPCICard', '{}'.format(caps.ulPCICard))
        print('ulEMGainCapability', '{:020b}'.format(caps.ulEMGainCapability))
        print('ulFTReadModes', '{:06b}'.format(caps.ulFTReadModes))

    def _get_detector_dimensions(self):
        '''
		gets the dimensions of the detector
		'''
        detector_width = c.c_int()
        detector_height = c.c_int()
        dll.GetDetector(c.byref(detector_width), c.byref(detector_height))
        self.info.width = detector_width.value
        self.info.height = detector_height.value
        return [self.info.width, self.info.height]

    def get_temperature_range(self):
        '''
		gets the range of available temperatures
		'''
        min_temp = c.c_int()
        max_temp = c.c_int()
        dll.GetTemperatureRange(c.byref(min_temp), c.byref(max_temp))
        self.info.min_temp = min_temp.value
        self.info.max_temp = max_temp.value
        return [self.info.min_temp, self.info.max_temp]

    def get_cooler_state(self):
        '''
		reads the state of the cooler
		'''
        cooler_state = c.c_int()
        error = dll.IsCoolerOn(c.byref(cooler_state))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.cooler_state = bool(cooler_state)
            return self.info.cooler_state
        else:
            raise Exception(ERROR_CODE[error])

    def set_cooler_on(self):
        '''
		turns on cooling
		'''
        error = dll.CoolerON()
        if not (ERROR_CODE[error] == 'DRV_SUCCESS'):
            raise Exception(ERROR_CODE[error])

    def set_cooler_off(self):
        '''
		turns off cooling
		'''
        error = dll.CoolerOFF()
        if not (ERROR_CODE[error] == 'DRV_SUCCESS'):
            raise Exception(ERROR_CODE[error])

    def get_temperature(self):
        temperature = c.c_int()
        error = dll.GetTemperature(c.byref(temperature))
        if (ERROR_CODE[error] == 'DRV_TEMP_STABILIZED' or ERROR_CODE[error] == 'DRV_TEMP_NOT_REACHED' or ERROR_CODE[
            error] == 'DRV_TEMP_DRIFT' or ERROR_CODE[error] == 'DRV_TEMP_NOT_STABILIZED'):
            self.info.temperature = temperature.value
            return temperature.value
        else:
            raise Exception(ERROR_CODE[error])

    def set_temperature(self, temperature):
        temperature = c.c_int(int(temperature))
        error = dll.SetTemperature(temperature)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.temperature_setpoint = temperature.value
        else:
            raise Exception(ERROR_CODE[error])

    def acquire_camera_serial_number(self):
        serial_number = c.c_int()
        error = dll.GetCameraSerialNumber(c.byref(serial_number))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.serial_number = serial_number.value
        else:
            raise Exception(ERROR_CODE[error])

    def get_camera_serial_number(self):
        return self.info.serial_number

    def get_camera_em_gain_range(self):
        min_gain = c.c_int()
        max_gain = c.c_int()
        error = dll.GetEMGainRange(c.byref(min_gain), c.byref(max_gain))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.min_gain = min_gain.value
            self.info.max_gain = max_gain.value
            return (min_gain.value, max_gain.value)
        else:
            raise Exception(ERROR_CODE[error])

    def get_emccd_gain(self):
        gain = c.c_int()
        error = dll.GetEMCCDGain(c.byref(gain))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.emccd_gain = gain.value
            return gain.value
        else:
            raise Exception(ERROR_CODE[error])

    def set_emccd_gain(self, gain):
        error = dll.SetEMCCDGain(c.c_int(int(gain)))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.emccd_gain = gain
        else:
            raise Exception(ERROR_CODE[error])

    def set_read_mode(self, mode):
        try:
            mode_number = READ_MODE[mode]
        except KeyError:
            raise Exception("Incorrect read mode {}".format(mode))
        error = dll.SetReadMode(c.c_int(mode_number))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.read_mode = mode
        else:
            raise Exception(ERROR_CODE[error])

    def get_read_mode(self):
        return self.info.read_mode

    def set_acquisition_mode(self, mode):
        try:
            mode_number = AcquisitionMode[mode]
        except KeyError:
            raise Exception("Incorrect acquisition mode {}".format(mode))
        error = dll.SetAcquisitionMode(c.c_int(mode_number))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.acquisition_mode = mode
        else:
            raise Exception(ERROR_CODE[error])

    def get_acquisition_mode(self):
        return self.info.acquisition_mode

    def set_trigger_mode(self, mode):
        try:
            mode_number = TriggerMode[mode]
        except KeyError:
            raise Exception("Incorrect trigger mode {}".format(mode))
        error = dll.SetTriggerMode(c.c_int(mode_number))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.trigger_mode = mode
        else:
            raise Exception(ERROR_CODE[error])

    def get_trigger_mode(self):
        return self.info.trigger_mode

    def set_exposure_time(self, time):
        error = dll.SetExposureTime(c.c_float(time))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.get_acquisition_timings()
        else:
            raise Exception(ERROR_CODE[error])

    def get_exposure_time(self):
        return self.info.exposure_time

    def get_acquisition_timings(self):
        exposure = c.c_float()
        accumulate = c.c_float()
        kinetic = c.c_float()
        error = dll.GetAcquisitionTimings(c.byref(exposure), c.byref(accumulate), c.byref(kinetic))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.exposure_time = exposure.value
            self.info.accumulate_cycle_time = accumulate.value
            self.info.kinetic_cycle_time = kinetic.value
        else:
            raise Exception(ERROR_CODE[error])

    def set_image(self, hbin, vbin, hstart, hend, vstart, vend):
        hbin = int(hbin);
        vbin = int(vbin);
        hstart = int(hstart);
        hend = int(hend);
        vstart = int(vstart);
        vend = int(vend)
        error = dll.SetImage(c.c_int(hbin), c.c_int(vbin), c.c_int(hstart), c.c_int(hend), c.c_int(vstart),
                             c.c_int(vend))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.image_region = [hbin, vbin, hstart, hend, vstart, vend]
        else:
            raise Exception(ERROR_CODE[error])

    def get_image(self):
        return self.info.image_region

    def set_shutter(self, pol, mode, closeTime=0, openTime=0):
        error = dll.SetShutter(pol, mode, closeTime, openTime)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            pass
        else:
            raise Exception(ERROR_CODE[error])

    def start_acquisition(self):
        error = dll.StartAcquisition()
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            return
        else:
            raise Exception(ERROR_CODE[error])

    def wait_for_acquisition(self):
        error = dll.WaitForAcquisition()
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            return True
        elif (ERROR_CODE[error] == 'DRV_NO_NEW_DATA'):
            return False
        else:
            raise Exception(ERROR_CODE[error])

    def cancel_wait(self):
        error = dll.CancelWait()
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            return
        else:
            raise Exception(ERROR_CODE[error])

    def abort_acquisition(self):
        error = dll.AbortAcquisition()
        if (ERROR_CODE[error] in ['DRV_SUCCESS', 'DRV_IDLE']):
            return
        else:
            raise Exception(ERROR_CODE[error])

    def get_acquired_data(self, num_images):
        hbin, vbin, hstart, hend, vstart, vend = self.info.image_region

        iWidth = int((hend - hstart + 1) / float(hbin))
        iHeight = int((vend - vstart + 1) / float(vbin))

        dim = int(num_images * iWidth * iHeight)
        image_struct = c.c_int * dim
        data = image_struct()
        error = dll.GetAcquiredData(c.pointer(data), dim)

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            data = data[:]

            image = np.reshape(data, (num_images, iHeight, iWidth))
            return image
        elif ERROR_CODE[error] == 'DRV_NO_NEW_DATA':
            return np.array([])
        else:
            raise Exception(ERROR_CODE[error])

    def get_most_recent_image(self):
        hbin, vbin, hstart, hend, vstart, vend = self.info.image_region

        iWidth = int((hend - hstart + 1) / float(hbin))
        iHeight = int((vend - vstart + 1) / float(vbin))

        dim = int(iWidth * iHeight)
        image_struct = c.c_int * dim
        data = image_struct()
        error = dll.GetMostRecentImage(c.pointer(data), dim)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            data = data[:]
            image = np.reshape(data, (iHeight, iWidth))
            return image
        elif ERROR_CODE[error] == 'DRV_NO_NEW_DATA':
            return np.array([])
        else:
            raise Exception(ERROR_CODE[error])

    def set_number_accumulations(self, numAcc):
        error = dll.SetNumberAccumulations(c.c_int(int(numAcc)))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.number_accumulations = numAcc
        else:
            raise Exception(ERROR_CODE[error])

    def get_number_accumulations(self):
        return self.info.number_accumulations

    def set_accumulation_cycle_time(self, acTime):
        error = dll.SetAccumulationCycleTime(c.c_float(float(acTime)))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            pass
        else:
            raise Exception(ERROR_CODE[error])

    def set_number_kinetics(self, numKin):
        error = dll.SetNumberKinetics(c.c_int(int(numKin)))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            self.info.number_kinetics = numKin
        else:
            raise Exception(ERROR_CODE[error])

    def get_number_kinetics(self):
        return self.info.number_kinetics

    def set_kinetic_cycle_time(self, kcTime):
        error = dll.SetKineticCycleTime(c.c_float(float(kcTime)))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            pass
        else:
            raise Exception(ERROR_CODE[error])

    def get_status(self):
        status = c.c_int()
        error = dll.GetStatus(c.byref(status))
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            return ERROR_CODE[status.value]
        else:
            raise Exception(ERROR_CODE[error])

    def get_preamp_gains(self):
        n_gains = c.c_int()
        dll.GetNumberPreAmpGains(c.byref(n_gains))

        preamp_gains = []
        for i in range(n_gains.value):
            gain = c.c_float()
            dll.GetPreAmpGain(i, c.byref(gain))
            preamp_gains.append(round(gain.value, 1))

        return preamp_gains

    def set_preamp_gain(self, gain):
        error = dll.SetPreAmpGain(gain)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            return
        else:
            raise Exception(ERROR_CODE[error])

    def get_vs_speeds(self):
        n_vals = c.c_int()
        dll.GetNumberVSSpeeds(c.byref(n_vals))

        vertical_shift_speeds = []
        for i in range(n_vals.value):
            speed = c.c_float()
            dll.GetVSSpeed(i, c.byref(speed))
            vertical_shift_speeds.append(round(speed.value, 1))

        return vertical_shift_speeds

    def set_vs_speed(self, vs_speed):
        error = dll.SetVSSpeed(vs_speed)
        if ERROR_CODE[error] == 'DRV_SUCCESS':
            return
        else:
            raise Exception(ERROR_CODE[error])

    def set_output_amp(self, index):
        error = dll.SetOutputAmplifier(index)

        if ERROR_CODE[error] == 'DRV_SUCCESS':
            self.outamp = index
        else:
            raise Exception(ERROR_CODE[error])

    def get_hs_speeds(self, channel, outamp):
        n_vals = c.c_int()
        dll.GetNumberHSSpeeds(channel, outamp, c.byref(n_vals))

        horizontal_shift_speeds = []
        for i in range(n_vals.value):
            speed = c.c_float()
            dll.GetHSSpeed(channel, outamp, i, c.byref(speed))
            horizontal_shift_speeds.append(round(speed.value, 1))

        return horizontal_shift_speeds

    def set_hs_speed(self, hs_speed):
        error = dll.SetHSSpeed(self.outamp, hs_speed)
        if (ERROR_CODE[error] == 'DRV_SUCCESS'):
            return
        else:
            raise Exception(ERROR_CODE[error])

    def get_series_progress(self):
        acc = c.c_long()
        series = c.c_long()
        error = dll.GetAcquisitionProgress(c.byref(acc), c.byref(series))
        if ERROR_CODE[error] == "DRV_SUCCESS":
            return acc.value, series.value
        else:
            raise Exception(ERROR_CODE[error])

    def get_number_new_images(self):
        first = c.c_long()
        last = c.c_long()
        error = dll.GetNumberNewImages(c.byref(first), c.byref(last))
        if ERROR_CODE[error] == "DRV_SUCCESS":
            return first.value, last.value
        else:
            raise Exception(ERROR_CODE[error])

    def get_number_available_images(self):
        first = c.c_long()
        last = c.c_long()
        error = dll.GetNumberAvailableImages(c.byref(first), c.byref(last))
        if ERROR_CODE[error] == "DRV_SUCCESS":
            return first.value, last.value
        else:
            raise Exception(ERROR_CODE[error])

    def prepare_acqusition(self):
        error = dll.PrepareAcquisition()
        if ERROR_CODE[error] == "DRV_SUCCESS":
            return
        else:
            raise Exception(ERROR_CODE[error])

    def shut_down(self):
        error = dll.ShutDown()
        return error


ERROR_CODE = {
    20001: "DRV_ERROR_CODES",
    20002: "DRV_SUCCESS",
    20003: "DRV_VXNOTINSTALLED",
    20006: "DRV_ERROR_FILELOAD",
    20007: "DRV_ERROR_VXD_INIT",
    20010: "DRV_ERROR_PAGELOCK",
    20011: "DRV_ERROR_PAGE_UNLOCK",
    20013: "DRV_ERROR_ACK",
    20024: "DRV_NO_NEW_DATA",
    20026: "DRV_SPOOLERROR",
    20034: "DRV_TEMP_OFF",
    20035: "DRV_TEMP_NOT_STABILIZED",
    20036: "DRV_TEMP_STABILIZED",
    20037: "DRV_TEMP_NOT_REACHED",
    20038: "DRV_TEMP_OUT_RANGE",
    20039: "DRV_TEMP_NOT_SUPPORTED",
    20040: "DRV_TEMP_DRIFT",
    20050: "DRV_COF_NOTLOADED",
    20053: "DRV_FLEXERROR",
    20066: "DRV_P1INVALID",
    20067: "DRV_P2INVALID",
    20068: "DRV_P3INVALID",
    20069: "DRV_P4INVALID",
    20070: "DRV_INIERROR",
    20071: "DRV_COERROR",
    20072: "DRV_ACQUIRING",
    20073: "DRV_IDLE",
    20074: "DRV_TEMPCYCLE",
    20075: "DRV_NOT_INITIALIZED",
    20076: "DRV_P5INVALID",
    20077: "DRV_P6INVALID",
    20083: "P7_INVALID",
    20089: "DRV_USBERROR",
    20091: "DRV_NOT_SUPPORTED",
    20099: "DRV_BINNING_ERROR",
    20990: "DRV_NOCAMERA",
    20991: "DRV_NOT_SUPPORTED",
    20992: "DRV_NOT_AVAILABLE"
}

READ_MODE = {
    'Full Vertical Binning': 0,
    'Multi-Track': 1,
    'Random-Track': 2,
    'Sinle-Track': 3,
    'Image': 4
}

AcquisitionMode = {
    'Single Scan': 1,
    'Accumulate': 2,
    'Kinetics': 3,
    'Fast Kinetics': 4,
    'Run till abort': 5
}

TriggerMode = {
    'Internal': 0,
    'External': 1,
    'External Start': 6,
    'External Exposure': 7,
    'External FVB EM': 9,
    'Software Trigger': 10,
    'External Charge Shifting': 12
}

if __name__ == '__main__':

    print('{} cameras available'.format(get_available_cameras()))

    camera = AndorCamera()
    camera.print_software_version()
    camera.print_get_capabilities()

    gains = camera.get_preamp_gains()

    print('#, Gains')
    for idx, gain in enumerate(gains):
        print('{:d}, {:.2f}'.format(idx, gain))

    channel = 0
    outamp = 0
    speeds = camera.get_hs_speeds(channel, outamp)

    print('#, HSS')
    for idx, speed in enumerate(speeds):
        print('{:d}, {:.3f}'.format(idx, speed))

    speeds = camera.get_vs_speeds()

    print('#, VSS')
    for idx, speed in enumerate(speeds):
        print('{:d}, {:.3f}'.format(idx, speed))

    del camera