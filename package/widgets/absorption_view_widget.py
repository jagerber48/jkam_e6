import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from package.ui.absorption_view_widget_ui import Ui_AbsorptionViewWidget
from package.ui.absorption_parameters_widget_ui import Ui_AbsorptionParametersWidget
from package.widgets.AnalysisWidgets import AbsorptionAnalyzer


class AbsorptionViewWidget(QWidget, Ui_AbsorptionViewWidget):
    analysis_complete_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(AbsorptionViewWidget, self).__init__(parent=parent)
        self.setupUi(self)
        self.parameters_window = None

        self.editor_list = [self.N_view_editor,
                            self.OD_view_editor,
                            self.atom_view_editor,
                            self.bright_view_editor,
                            self.dark_view_editor]

        for editor in self.editor_list:
            image_view = editor.imageview
            image_view.getView().setXLink(self.N_view_editor.imageview.getView())
            image_view.getView().setYLink(self.N_view_editor.imageview.getView())


        self.analyzer = None
        self.analyzer_loaded = False
        self.frame_count = 0
        self.atom_frame = None
        self.bright_frame = None
        self.dark_frame = None
        self.od_frame = None
        self.number_frame = None

    def process_frame(self, frame):
        self.frame_count += 1
        if self.frame_count == 1:
            self.atom_frame = frame
            image_view = self.atom_view_editor.imageview
            image_view.setImage(frame, autoRange=False, autoLevels=False, autoHistogramRange=False)
        elif self.frame_count == 2:
            self.bright_frame = frame
            image_view = self.bright_view_editor.imageview
            image_view.setImage(frame, autoRange=False, autoLevels=False, autoHistogramRange=False)
        elif self.frame_count == 3:
            self.dark_frame = frame
            image_view = self.dark_view_editor.imageview
            image_view.setImage(frame, autoRange=False, autoLevels=False, autoHistogramRange=False)

            self.od_frame, self.number_frame = self.analyzer.absorption_od_and_number(self.atom_frame,
                                                                                      self.bright_frame,
                                                                                      self.dark_frame)

            image_view = self.OD_view_editor.imageview
            image_view.setImage(self.od_frame, autoRange=False, autoLevels=False,
                                autoHistogramRange=False)

            image_view = self.N_view_editor.imageview
            image_view.setImage(self.number_frame, autoRange=False, autoLevels=False,
                                autoHistogramRange=False)
            self.frame_count = 0
            self.analysis_complete_signal.emit()
        else:
            print('ERROR: too many frames')
            self.atom_frame = None
            self.bright_frame = None
            self.dark_frame = None
            self.od_frame = None
            self.number_frame = None
            self.frame_count = 0

    def load_analyzer(self, *, atom, imaging_system):
        self.analyzer = AbsorptionAnalyzer(atom=atom, imaging_system=imaging_system)
        self.parameters_window = AbsorptionParametersWidget(atom=atom, imaging_system=imaging_system)
        self.imaging_parameters_pushButton.connect(self.parameters_window.show)

        self.analyzer_loaded = True

    def unload_analyzer(self):
        del self.analyzer
        self.analyzer = None


class AbsorptionParametersWidget(QWidget, Ui_AbsorptionParametersWidget):
    def __init__(self, parent=None, *, atom, imaging_system, detuning=0, pulse_time=100e-6):
        super(AbsorptionParametersWidget, self).__init__(parent=parent)
        self.atom = atom
        self.imaging_system = imaging_system
        self.detuning = detuning
        self.pulse_time = pulse_time

    def set_atom_text(self):
        self.frequency_value_label.setText(f'{self.transition_frequency*1e-12:.1f} THz')
        self.cross_section_value_label.setText(f'{self.cross_section*1e4:.1f} cm<sup>2</sup>')
        self.isat_value_label.setText(f'{self.saturation_intensity*1e3/1e4:.1f} mW/cm<sup>2</sup>')
        self.linewidth_value_label.setText(f'{self.linewidth*1e-6:.1f} MHz')

    def set_imaging_sytem_text(self):
        pixel_size = np.sqrt(self.pixel_area) * 1e6  # micron
        self.pixel_value_label.setText(f'{pixel_size:.1f} um')
        self.magnification_value_label.setText(f'{self.magnification:.1f}')

    @property
    def atom(self):
        return self._atom

    @atom.setter
    def atom(self, atom):
        self._atom = atom
        self.cross_section = self._atom.cross_section
        self.linewidth = self._atom.linewidth
        self.saturation_intensity = self._atom.saturation_intensity
        self.transition_frequency = self._atom.transition_freq
        self.set_atom_text()

    @property
    def imaging_system(self):
        return self._imaging_system

    @imaging_system.setter
    def imaging_system(self, imaging_system):
        self._imaging_system = imaging_system
        self._imaging_system = imaging_system
        self.magnification = self._imaging_system.magnification
        self.pixel_area = self._imaging_system.camera_type.pixel_area
        self.count_conversion = self._imaging_system.camera_type.total_gain

    @property
    def detuning(self):
        return self._detuning

    @detuning.setter
    def detuning(self, value):
        self._detuning = value
        self.detuning_value_label.setText(f'{self._detuning*1e-6} MHz')

    @property
    def pulse_time(self):
        return self._pulse_time

    @pulse_time.setter
    def pulse_time(self, value):
        self._pulse_time = value
        self.pulse_value_label.setText(f'{self._pulse_time*1e6} us')
