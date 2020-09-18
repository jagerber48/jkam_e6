from enum import Enum
import numpy as np
from grasshopperdriver import GrasshopperDriver
from andordriver import AndorDriver


class GrasshopperCamera:
    driver = GrasshopperDriver()
    pixel_area = 6.45e-6**2
    quantum_efficiency = 0.38  # Number of electrons per photon
    adu_conversion = 1 / 0.37  # Number of digital counts per electron
    bit_conversion = 2**-8  # 16 bit camera output is converted to 8 bits before data is captured
    total_gain = bit_conversion * adu_conversion * quantum_efficiency  # Number of recoreded digital counts per photon


class SideImagingSystem:
    name = 'Side Imaging'
    camera_serial_number = '18431942'
    camera_type = GrasshopperCamera()
    magnification = 0.77


class SpareGrasshopper:
    name = 'Spare Grasshopper'
    camera_serial_number = '17491535'
    camera_type = GrasshopperCamera()
    magnification = 1  # Not Applicable


class VerticalImagingSystem:
    name = 'Spare Grasshopper'
    camera_serial_number = ''
    camera_type = AndorCamera()
    magnification = 50  # Not Applicable


class RbProperties:
    cross_section = 2.907e-13  # Steck Rubidium 87 D Line Data
    linewidth = 2 * np.pi * 6.07e6  # Steck Rubidium 87 D Line Data
    saturation_intensity = 1.67 * 1e4 / 1e3  # Steck Rubidium 87 D Line Data, convert mW/cm^2 to W/m^2
    d2_transition_freq = 2 * np.pi * 384.230e12


imaging_system_list = [SideImagingSystem(), SpareGrasshopper()]

    # grasshopper_sn = '17491535'  # Spare Camera for testing
