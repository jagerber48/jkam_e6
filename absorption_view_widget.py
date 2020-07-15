from absorption_view_widget_ui import Ui_AbsorptionViewWidget
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer
import pyqtgraph as pg


class AbsorptionViewWidget(QWidget, Ui_AbsorptionViewWidget):
    def __init__(self, parent=None):
        super(AbsorptionViewWidget, self).__init__(parent=parent)
        self.setupUi(self)
        # self.link_timer = QTimer()
        # self.link_timer.timeout.connect(self.link_views)

        self.editor_list = [self.N_view_editor,
                                self.OD_view_editor,
                                self.atom_view_editor,
                                self.bright_view_editor,
                                self.dark_view_editor]

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

        # self.link_timer.start(500)

    # def link_views(self):
    #     current_index = self.tabWidget.currentIndex()
    #     print(f'linking: {current_index}')
    #
    #     current_editor = self.editor_list[current_index]
    #     view_state = current_editor.imageview.getView().getState()
    #     for editor in self.editor_list:
    #         image_view = editor.imageview
    #         image_view.getView().setState(view_state)
    #         image_view.
