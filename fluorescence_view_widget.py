from ui_components.fluorescence_view_widget_ui import Ui_FluorescenceViewWidget
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
import pyqtgraph as pg
from AnalysisWidgets import AbsorptionAnalyzer


class FluorescenceViewWidget(QWidget, Ui_FluorescenceViewWidget):
    analysis_complete_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(FluorescenceViewWidget, self).__init__(parent=parent)
        self.setupUi(self)

        self.editor_list = [self.N_view_editor,
                            self.diff_view_editor,
                            self.atom_view_editor,
                            self.reference_view_editor]

        for editor in self.editor_list:
            image_view = editor.imageview
            image_view.ui.roiBtn.hide()
            image_view.ui.menuBtn.hide()
            vLine = pg.InfiniteLine(angle=90, movable=True)
            hLine = pg.InfiniteLine(angle=0, movable=True)
            image_view.addItem(vLine, ignoreBounds=True)
            image_view.addItem(hLine, ignoreBounds=True)
            image_view.getView().setXLink(self.N_view_editor.imageview.getView())
            image_view.getView().setYLink(self.N_view_editor.imageview.getView())

        self.analyzer = AbsorptionAnalyzer()
        self.frame_count = 0
        self.atom_frame = None
        self.ref_frame = None
        self.diff_frame = None
        self.number_frame = None

    def process_frame(self, frame):
        self.frame_count += 1
        if self.frame_count == 1:
            self.atom_frame = frame
            image_view = self.atom_view_editor.imageview
            image_view.setImage(self.atom_frame, autoRange=False, autoLevels=False, autoHistogramRange=False)
        elif self.frame_count == 2:
            self.ref_frame = frame
            image_view = self.reference_view_editor.imageview
            image_view.setImage(self.ref_frame, autoRange=False, autoLevels=False, autoHistogramRange=False)

            # self.diff_frame, self.number_frame = self.analyzer.absorption_od_and_number(self.atom_frame,
            #                                                                             self.ref_frame,
            #                                                                             self.dark_frame)

            self.diff_frame = self.atom_frame - self.ref_frame
            self.number_frame = 1 * self.diff_frame

            image_view = self.diff_view_editor.imageview
            image_view.setImage(self.diff_frame, autoRange=False, autoLevels=False,
                                autoHistogramRange=False)

            image_view = self.N_view_editor.imageview
            image_view.setImage(self.number_frame, autoRange=False, autoLevels=False,
                                autoHistogramRange=False)
            self.frame_count = 0
            self.analysis_complete_signal.emit()
        else:
            print('ERROR: too many frames')
            self.atom_frame = None
            self.ref_frame = None
            self.diff_frame = None
            self.number_frame = None
            self.frame_count = 0
