import numpy as np
from scipy.constants import hbar
from PyQt5.QtCore import QObject


class AbsorptionAnalyzer(QObject):
    # TODO: Implement input parameters for conversion parameters
    def __init__(self, *, atom, imaging_system, calc_high_sat=False):
        super(AbsorptionAnalyzer, self).__init__()
        self.atom = atom
        self.cross_section = self.atom.cross_section
        self.linewidth = self.atom.linewidth
        self.saturation_intensity = self.atom.saturation_intensity
        self.transition_frequency = self.atom.transition_freq

        self.imaging_system = imaging_system
        self.magnification = self.imaging_system.magnification
        self.pixel_area = self.imaging_system.camera_type.pixel_area
        self.count_conversion = self.imaging_system.camera_type.total_gain

    def absorption_od_and_number(self, atom_frame, bright_frame, dark_frame):
        atom_counts, bright_counts = self.absorption_bg_subtract(atom_frame, bright_frame, dark_frame)
        optical_density = self.optical_density_analysis(atom_counts, bright_counts)
        atom_number = self.atom_count_analysis(atom_counts, bright_counts, optical_density, calc_high_sat=True)
        return optical_density, atom_number

    @staticmethod
    def absorption_bg_subtract(atom_frame, bright_frame, dark_frame):
        atom_counts = atom_frame - dark_frame
        bright_counts = bright_frame - dark_frame
        return atom_counts, bright_counts

    @staticmethod
    def optical_density_analysis(atom_counts, bright_counts):
        """
        Calculate transmissivity and optical density. Note that data is rejected if atom_counts > bright counts or
        if either one is negative. These conditions can arise due noise in the beams including shot noise or
        temporal fluctuations in beam powers. This seems like the easiest way to handle these edge cases but it could
        lead to biases in atom number estimations.
        """
        transmissivity = np.true_divide(atom_counts, bright_counts,
                                        out=np.full_like(atom_counts, 0, dtype=float),
                                        where=np.logical_and(atom_counts > 0, bright_counts > 0))
        optical_density = -1 * np.log(transmissivity, out=np.full_like(atom_counts, np.nan, dtype=float),
                                      where=np.logical_and(0 < transmissivity, transmissivity <= 1))
        return optical_density

    def atom_count_analysis(self, atom_counts, bright_counts, optical_density=None, calc_high_sat=True):
        if optical_density is None:
            optical_density = self.optical_density_analysis(atom_counts, bright_counts)
        low_sat_atom_number = self.atom_count_analysis_below_sat(optical_density)
        if calc_high_sat:
            high_sat_atom_number = self.atom_count_analysis_above_sat(atom_counts, bright_counts)
        else:
            high_sat_atom_number = 0
        atom_number = low_sat_atom_number + high_sat_atom_number
        return atom_number

    def atom_count_analysis_below_sat(self, optical_density,
                                      detuning=0):
        detuning_factor = 1 + (2 * detuning / self.linewidth) ** 2
        column_density_below_sat = (detuning_factor / self.cross_section) * optical_density
        column_area = self.pixel_area / self.magnification**2  # size of a pixel in object plane
        column_number = column_area * column_density_below_sat
        return column_number

    def atom_count_analysis_above_sat(self, atom_counts, bright_counts, image_pulse_time=100e-6,
                                      efficiency_path=1.0):
        # convert counts to detected photons
        atom_photons_det = atom_counts / self.count_conversion
        bright_photons_det = bright_counts / self.count_conversion

        # convert detected photons to detected intensity
        atom_intensity_det = (atom_photons_det *
                              (hbar * self.transition_frequency) / (self.pixel_area * image_pulse_time))
        bright_intensity_det = (bright_photons_det *
                                (hbar * self.transition_frequency) / (self.pixel_area * image_pulse_time))

        # convert detected intensity to intensity before and after atoms
        intensity_out = atom_intensity_det / efficiency_path / self.magnification**2
        intensity_in = bright_intensity_det / efficiency_path / self.magnification**2

        # convert intensity in and out to resonant saturation parameter in and out
        s0_out = intensity_out / self.saturation_intensity
        s0_in = intensity_in / self.saturation_intensity

        # calculate column density from s0_in and s0_out
        column_density = (s0_in - s0_out) / self.cross_section

        # calculate column atom number from column_density and column_area
        column_area = self.pixel_area / self.magnification**2  # size of a pixel in the object plane
        column_number = column_density * column_area
        return column_number
