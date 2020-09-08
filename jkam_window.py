from enum import Enum
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QIcon
from ui_components.camerawindow_ui import Ui_CameraWindow
from AnalysisWidgets import PlotHistoryAnalyzer, RoiIntegrationAnalyzer


class ImagingMode(Enum):
    VIDEO = 0
    ABSORPTION = 1


class JKamWindow(QMainWindow, Ui_CameraWindow):

    def __init__(self):
        super(JKamWindow, self).__init__()
        self.setupUi(self)

        self.data = None

        self.frame_received_signal = self.camera_control_widget.frame_received_signal
        self.frame_received_signal.connect(self.on_capture)

        # self.history_image_view = self.videovieweditor.imageview
        self.plothistoryanalyzer = PlotHistoryAnalyzer(RoiIntegrationAnalyzer(self.videovieweditor.imageview))
        self.roi_analyzer_checkBox.clicked.connect(self.toggle_analyzer_window)

        self.imaging_mode = None
        self.camera_control_widget.absorption_radioButton.clicked.connect(self.set_mode)
        self.camera_control_widget.video_radioButton.clicked.connect(self.set_mode)
        self.set_mode()

        self.absorption_frame_count = 0
        self.atom_frame = None
        self.bright_frame = None
        self.dark_frame = None
        self.optical_density_frame = None
        self.atom_number_frame = None

    def set_mode(self):
        # try:
        #     self.history_image_view.removeItem(self.plothistoryanalyzer.roi)
        # except AttributeError:
        #     pass
        # self.plothistoryanalyzer.clear()

        if self.camera_control_widget.video_radioButton.isChecked():
            self.view_stackedWidget.setCurrentIndex(0)
            self.plothistoryanalyzer.analyzer.set_imageview(self.videovieweditor.imageview)
            # self.history_image_view = self.videovieweditor.imageview
            # self.history_widget.setup_figure(self.history_image_view)
            self.imaging_mode = ImagingMode.VIDEO
        elif self.camera_control_widget.absorption_radioButton.isChecked():
            # self.history_image_view = self.absorption_view_widget.N_view_editor.imageview
            # self.history_widget.setup_figure(self.history_image_view)
            self.view_stackedWidget.setCurrentIndex(1)
            self.plothistoryanalyzer.analyzer.set_imageview(self.absorption_view_widget.N_view_editor.imageview)
            self.imaging_mode = ImagingMode.ABSORPTION

    def on_capture(self, frame):
        self.frame_received_signal.disconnect(self.on_capture)
        if self.imaging_mode == ImagingMode.VIDEO:
            self.display_video_frame(frame)
        elif self.imaging_mode == ImagingMode.ABSORPTION:
            self.display_absorption_frame(frame)
        self.frame_received_signal.connect(self.on_capture)

    def display_video_frame(self, frame):
        image_view = self.videovieweditor.imageview
        image_view.setImage(frame, autoRange=False,
                            autoLevels=False, autoHistogramRange=False)
        self.plothistoryanalyzer.analysis_request_signal.emit()
        # self.history_widget.analyze_signal.emit(frame, image_view.getImageItem())

    def display_absorption_frame(self, frame):
        self.absorption_view_widget.process_frame(frame)
        image_view = self.absorption_view_widget.N_view_editor.imageview
        data = self.absorption_view_widget.number_frame
        # self.history_widget.analyze_signal.emit(data, image_view.getImageItem())

    def toggle_analyzer_window(self):
        if self.roi_analyzer_checkBox.isChecked():
            self.plothistoryanalyzer.plothistorywidget.show()
            self.plothistoryanalyzer.enable()
        else:
            self.plothistoryanalyzer.plothistorywidget.close()
            self.plothistoryanalyzer.disable()

    def closeEvent(self, event):
        self.camera_control_widget.close()
        sys.exit()


# Start Qt event loop unless running in interactive mode.
def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('favicon.ico'))
    ex = JKamWindow()
    ex.show()
    app.exec_()


if __name__ == '__main__':
    main()
    sys.exit()
