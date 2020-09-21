from PyQt5.QtWidgets import QWidget
from package.ui.imagecapturemodewidget_ui import Ui_ImageCaptureModeWidget


class ImageCaptureModeWidget(QWidget, Ui_ImageCaptureModeWidget):
    def __init__(self, parent=None):
        super(ImageCaptureModeWidget, self).__init__(parent=parent)
        self.setupUi()