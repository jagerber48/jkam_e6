from ui_components.absorption_view_widget_ui import Ui_AbsorptionViewWidget
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from AnalysisWidgets import AbsorptionAnalyzer


class AbsorptionViewWidget(QWidget, Ui_AbsorptionViewWidget):
    analysis_complete_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(AbsorptionViewWidget, self).__init__(parent=parent)
        self.setupUi(self)

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
        self.analyzer_loaded = True

    def unload_analyzer(self):
        del self.analyzer
        self.analyzer = None
