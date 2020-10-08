from package.widgets.imagevieweditor import ImageViewEditor
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal


class MultishotViewWidget(QtWidgets.QWidget):
    analysis_complete_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(MultishotViewWidget, self).__init__(parent=parent)
        self.setupUi()

        self.tab_list = []
        self.editor_list = []
        self.frame_list = []
        self.n_frames = 0
        self.curr_frame = 0

    def link_views(self, shared_view_index=0):
        shared_editor_view = self.editor_list[shared_view_index].imageview.getView()
        for editor in self.editor_list:
            image_view = editor.imageview.getView()
            image_view.setXLink(shared_editor_view)
            image_view.setYLink(shared_editor_view)
            editor.camview.crosshair_moved_signal.connect(self.share_crosshair)

    def share_crosshair(self, evt):
        for editor in self.editor_list:
            editor.camview.mouse_moved(evt, signal=False)

    def reset(self):
        self.curr_frame = 0

    def process_frame(self, frame):
        self.frame_list[self.curr_frame] = frame
        self.editor_list[self.curr_frame].setImage(frame, autoRange=False, autoLevels=False,
                                                   autoHistogramRange=False)
        self.curr_frame += 1
        if self.curr_frame == self.n_frames:
            self.curr_frame = 0
            self.analysis_complete_signal.emit()

    def setup_frames(self, num_frames):
        self.clear_tabs()
        for ind in range(num_frames):
            self.create_tab()

    def create_tab(self):
        self.n_frames += 1
        new_tab = QtWidgets.QWidget()
        self.tab_list.append(new_tab)
        new_tab_index = self.n_frames - 1
        gridLayout = QtWidgets.QGridLayout(new_tab)
        new_view_editor = ImageViewEditor(new_tab)
        gridLayout.addWidget(new_view_editor, 0, 0, 1, 1)
        self.editor_list.append(new_view_editor)
        self.frame_list.append(None)
        self.tabWidget.addTab(new_tab, f'Frame {new_tab_index:d}')
        self.link_views()

    def clear_tabs(self):
        self.tabWidget.clear()
        self.tab_list = []
        self.editor_list = []
        self.frame_list = []
        self.n_frames = 0
        self.curr_frame = 0

    def setupUi(self):
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setEnabled(True)
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.tabWidget.setCurrentIndex(0)


