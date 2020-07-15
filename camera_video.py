import sys
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from camerawindow_ui import Ui_CameraWindow


class CameraWindow(QtWidgets.QMainWindow, Ui_CameraWindow):
    grasshopper_sn = '17491535'

    def __init__(self):
        super(CameraWindow, self).__init__()
        self.setupUi(self)

        self.driver = self.camera_control_widget.driver
        self.data = None

        self.imageview_widget = self.imageview_widget.imageview
        self.history_widget.setup_figure(self.imageview_widget)
        # self.gaussfit_pushButton.clicked.connect(self.fit)
        self.driver.captured_signal.connect(self.on_capture)

    def on_capture(self, image):
        if self.driver.acquiring:
            self.driver.captured_signal.disconnect(self.on_capture)
            self.data = image
            self.imageview_widget.setImage(self.data, autoRange=False,
                                           autoLevels=False, autoHistogramRange=False)
            self.history_widget.analyze_signal.emit(self, self.imageview_widget.getImageItem())
            self.driver.captured_signal.connect(self.on_capture)

    def closeEvent(self, event):
        self.driver.close_connection()


# Start Qt event loop unless running in interactive mode.
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QIcon('favicon.ico'))
    ex = CameraWindow()
    ex.show()
    app.exec_()


if __name__ == '__main__':
    main()
    sys.exit()
