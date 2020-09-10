import numpy as np
from scipy.constants import hbar
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, QObject, pyqtSignal
import pyqtgraph as pg
from ui_components.plothistorywidget_ui import Ui_PlotHistoryWidget


class AbsorptionAnalyzer(QObject):

    RB_CROSS_SECTION = 2.907e-13  # Steck Rubidium 87 D Line Data
    RB_LINEWIDTH = 2 * np.pi * 6.07e6  # Steck Rubidium 87 D Line Data
    RB_SATURATION_INTENSITY = 1.67 * 1e4 / 1e3  # Steck Rubidium 87 D Line Data, convert mW/cm^2 to W/m^2
    RB_D2_FREQUENCY = 2 * np.pi * 384.230e12

    SIDE_IMAGING_MAGNIFICATION = 0.77
    GRASSHOPPER_PIXEL_AREA = 6.45e-6**2
    GRASSHOPPER_GTOT = (2**-8 / 0.37) * 0.38
    # Multiply incident photon number by quantum efficiency = 0.38, divide by ADU gain: 0.37 e-/ADU and
    # truncate 8 least significant bits to turn 16-bit camera output to 8-bit data received at computer

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

    @staticmethod
    def atom_count_analysis(atom_counts, bright_counts, optical_density=None, calc_high_sat=True):
        if optical_density is None:
            optical_density = AbsorptionAnalyzer.optical_density_analysis(atom_counts, bright_counts)
        low_sat_atom_number = AbsorptionAnalyzer.atom_count_analysis_below_sat(optical_density)
        if calc_high_sat:
            high_sat_atom_number = AbsorptionAnalyzer.atom_count_analysis_above_sat(atom_counts, bright_counts)
        else:
            high_sat_atom_number = 0
        atom_number = low_sat_atom_number + high_sat_atom_number
        return atom_number

    @staticmethod
    def atom_count_analysis_below_sat(optical_density, cross_section=RB_CROSS_SECTION,
                                      detuning=0, gamma=RB_LINEWIDTH,
                                      pixel_size=GRASSHOPPER_PIXEL_AREA,
                                      magnification=SIDE_IMAGING_MAGNIFICATION):
        detuning_factor = 1 + (2 * detuning / gamma)**2
        column_density_below_sat = (detuning_factor / cross_section) * optical_density
        column_area = pixel_size / magnification  # size of a pixel in object plane
        column_number = column_area * column_density_below_sat
        return column_number

    @staticmethod
    def atom_count_analysis_above_sat(atom_counts, bright_counts, image_pulse_time=100e-6,
                                      imaging_frequency=RB_D2_FREQUENCY,
                                      pixel_size=GRASSHOPPER_PIXEL_AREA,
                                      magnification=SIDE_IMAGING_MAGNIFICATION,
                                      efficiency_path=1.0,
                                      camera_gain=GRASSHOPPER_GTOT,
                                      saturation_intensity=RB_SATURATION_INTENSITY,
                                      cross_section=RB_CROSS_SECTION):
        # convert counts to detected photons
        atom_photons_det = atom_counts / camera_gain
        bright_photons_det = bright_counts / camera_gain

        # convert detected photons to detected intensity
        atom_intensity_det = atom_photons_det * (hbar * imaging_frequency) / (pixel_size * image_pulse_time)
        bright_intensity_det = bright_photons_det * (hbar * imaging_frequency) / (pixel_size * image_pulse_time)

        # convert detected intensity to intensity before and after atoms
        intensity_out = atom_intensity_det / efficiency_path / magnification
        intensity_in = bright_intensity_det / efficiency_path / magnification

        # convert intensity in and out to resonant saturation parameter in and out
        s0_out = intensity_out / saturation_intensity
        s0_in = intensity_in / saturation_intensity

        # calculate column density from s0_in and s0_out
        column_density = (s0_in - s0_out) / cross_section

        # calculate column atom number from column_density and column_area
        column_area = pixel_size / magnification  # size of a pixel in the object plane
        column_number = column_density * column_area
        return column_number


class RoiIntegrationAnalyzer(QObject):
    analysis_complete_signal = pyqtSignal(object)

    def __init__(self, imageview: AbsorptionAnalyzer):
        super(RoiIntegrationAnalyzer, self).__init__()
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.start()
        self.imageview = imageview
        self.roi = None
        self.create_roi()
        self.analyzing = False

    def set_imageview(self, imageview):
        self.remove_roi()
        self.imageview = imageview
        self.create_roi()

    def create_roi(self):
        del self.roi
        self.roi = pg.RectROI((200, 200), (200, 200), pen='w')
        self.roi.addScaleHandle([1, 1], [0, 0])
        self.roi.addScaleHandle([0, 0], [1, 1])
        self.imageview.addItem(self.roi)

    def analyze(self):
        self.analyzing = True
        roi_data = self.roi.getArrayRegion(self.imageview.image, self.imageview.getImageItem())
        roi_sum = np.nansum(roi_data)
        self.analysis_complete_signal.emit(roi_sum)
        self.analyzing = False

    def remove_roi(self):
        try:
            self.imageview.removeItem(self.roi)
        except AttributeError:
            pass


class PlotHistoryAnalyzer(QObject):
    analysis_request_signal = pyqtSignal()
    analyze_signal = pyqtSignal()

    def __init__(self, analyzer, label='counts', num_history=200):
        super(PlotHistoryAnalyzer, self).__init__()
        self.analyzer = analyzer
        self.plothistorywidget = PlotHistoryWidget(label=label, num_history=num_history)
        self.analyzer.analysis_complete_signal.connect(self.plothistorywidget.append_data)
        self.analyze_signal.connect(self.analyzer.analyze)
        self.analyzing = False

    def analyze(self):
        if not self.analyzer.analyzing:
            self.analyze_signal.emit()

    def enable(self):
        self.analysis_request_signal.connect(self.analyze)

    def disable(self):
        self.analysis_request_signal.disconnect(self.analyze)

    def clear(self):
        self.analyzer.remove_roi()


class PlotHistoryWidget(QtWidgets.QWidget, Ui_PlotHistoryWidget):
    """
    Rolling History Widget. pyqtgraph with the main functionality of providing a rolling history of data which has
    been loaded in through the "append_data" method.
    """
    def __init__(self, label='counts', num_history=200):
        super(PlotHistoryWidget, self).__init__()
        self.setupUi(self)

        self.label = label
        self.num_history = num_history
        self.history = np.zeros(self.num_history)
        self.history_min = self.history.min()
        self.history_max = self.history.max()

        self.history_PlotWidget.disableAutoRange()
        self.history_plot = self.history_PlotWidget.plot()
        self.history_plot.setPen(width=2)
        self.history_PlotWidget.setXRange(0, self.num_history)

        plot_item = self.history_PlotWidget.getPlotItem()
        plot_item.showGrid(x=True, y=True)
        plot_item.getAxis('bottom').setGrid(255)
        plot_item.getAxis('left').setGrid(255)
        plot_item.setLabel('bottom', text='Frame')
        plot_item.setLabel('left', text=self.label)

        self.set_min_pushButton.clicked.connect(self.set_min)
        self.clear_pushButton.clicked.connect(self.clear_history)
        self.set_max_pushButton.clicked.connect(self.set_max)

    def append_data(self, data):
        self.history = np.roll(self.history, -1)
        self.history[-1] = data
        self.plot()
        self.data_label.setText(f'{data:.3e}')

    def clear_history(self):
        self.history[:] = 0
        self.plot()

    def set_min(self):
        self.history_min = self.history.min()
        self.history_PlotWidget.setYRange(self.history_min, self.history_max)

    def set_max(self):
        self.history_max = self.history.max()
        self.history_PlotWidget.setYRange(self.history_min, self.history_max)

    def plot(self):
        self.history_plot.setData(self.history)
        self.history_PlotWidget.setYRange(self.history_min, self.history_max)
