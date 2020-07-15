from absorption_view_widget_ui import Ui_AbsorptionViewWidget
from PyQt5.QtWidgets import QWidget
import pyqtgraph as pg


class AbsorptionViewWidget(QWidget, Ui_AbsorptionViewWidget):
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
            image_view.ui.roiBtn.hide()
            image_view.ui.menuBtn.hide()
            vLine = pg.InfiniteLine(angle=90, movable=True)
            hLine = pg.InfiniteLine(angle=0, movable=True)
            image_view.addItem(vLine, ignoreBounds=True)
            image_view.addItem(hLine, ignoreBounds=True)