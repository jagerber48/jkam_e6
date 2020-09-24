from package.ui.fluorescence_view_widget_ui import Ui_FluorescenceViewWidget
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal


class FluorescenceViewWidget(QWidget, Ui_FluorescenceViewWidget):
    # TODO: Parameter View
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
            image_view.getView().setXLink(self.N_view_editor.imageview.getView())
            image_view.getView().setYLink(self.N_view_editor.imageview.getView())
            editor.camview.crosshair_moved_signal.connect(self.share_crosshair)

        self.analyzer = None
        self.frame_count = 0
        self.atom_frame = None
        self.ref_frame = None
        self.diff_frame = None
        self.number_frame = None

    def share_crosshair(self, evt):
        for editor in self.editor_list:
            editor.camview.mouse_moved(evt, signal=False)

    def process_frame(self, frame):
        self.frame_count += 1
        if self.frame_count == 1:
            self.atom_frame = frame
            self.atom_view_editor.setImage(self.atom_frame, autoRange=False, autoLevels=False,
                                           autoHistogramRange=False)
        elif self.frame_count == 2:
            self.ref_frame = frame
            self.reference_view_editor.setImage(self.ref_frame, autoRange=False, autoLevels=False,
                                                autoHistogramRange=False)

            self.diff_frame = self.atom_frame - self.ref_frame
            self.number_frame = 1 * self.diff_frame

            self.diff_view_editor.setImage(self.diff_frame, autoRange=False, autoLevels=False,
                                           autoHistogramRange=False)

            self.N_view_editor.setImage(self.number_frame, autoRange=False, autoLevels=False,
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
