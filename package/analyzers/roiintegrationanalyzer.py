import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget
import pyqtgraph as pg
from package.widgets.plothistorywindow import PlotHistoryWindow
from package.ui.roianalyzer_ui import Ui_RoiAnalyzer


class RoiIntegrationWorker(QThread):
    analysis_complete_signal = pyqtSignal(float)

    def __init__(self):
        super(RoiIntegrationWorker, self).__init__()
        self.imageview = None
        self.roi_sig = None
        self.roi_bg = None
        self.bg_subtract = False

    def run(self):
        roi_slice = self.roi_sig.getArraySlice(self.imageview.image, self.imageview.getImageItem())[0]
        roi_sig_data = self.imageview.image[roi_slice]
        roi_sig_sum = np.nansum(roi_sig_data)
        pixel_num_sig = roi_sig_data.size
        result = roi_sig_sum
        if self.roi_bg is not None and self.bg_subtract:
            roi_bg_slice = self.roi_bg.getArraySlice(self.imageview.image, self.imageview.getImageItem())[0]
            roi_bg_data = self.imageview.image[roi_bg_slice]
            pixel_num_bg = roi_bg_data.size
            roi_bg_mean = np.nansum(roi_bg_data) / pixel_num_bg
            result = roi_sig_sum - roi_bg_mean * pixel_num_sig
        self.analysis_complete_signal.emit(result)


class RoiIntegrationAnalyzer(QWidget, Ui_RoiAnalyzer):
    analyze_signal = pyqtSignal()

    def __init__(self, label='counts', num_history=200):
        super(RoiIntegrationAnalyzer, self).__init__()
        self.setupUi(self)
        self.analyzer = RoiIntegrationWorker()
        self.plothistorywindow = PlotHistoryWindow(label=label, num_history=num_history)
        self.plothistorywindow.window_close_signal.connect(self.window_closed)
        self.analyzer.analysis_complete_signal.connect(self.plothistorywindow.append_data)
        self.analyze_signal.connect(self.analyzer.run)
        self.enable_checkBox.clicked.connect(self.toggle_enable)
        self.bg_subtract_checkBox.clicked.connect(self.toggle_bg_subtract)

        self.imageview = None
        self.analyzer.imageview = self.imageview

        self.enabled = False
        self.bg_subtract = False

    def analyze(self):
        if self.enabled:
            self.analyzer.start()

    def enable(self):
        self.enabled = True
        self.analyzer.roi_sig = self.create_roi(pen='w')
        if self.bg_subtract:
            self.analyzer.roi_bg = self.create_roi(pen='r')

    def disable(self):
        self.enabled = False
        self.remove_sig_roi()
        self.remove_bg_roi()

    def enable_bg_subtract(self):
        self.bg_subtract = True
        self.analyzer.bg_subtract = self.bg_subtract
        if self.enabled:
            self.analyzer.roi_bg = self.create_roi(pen='r')

    def disable_bg_subtract(self):
        self.bg_subtract = False
        self.analyzer.bg_subtract = False
        if self.analyzer.roi_bg is not None:
            self.remove_bg_roi()

    def remove_sig_roi(self):
        try:
            self.analyzer.imageview.removeItem(self.analyzer.roi_sig)
            self.analyzer.roi_sig = None
        except AttributeError:
            pass

    def remove_bg_roi(self):
        try:
            self.analyzer.imageview.removeItem(self.analyzer.roi_bg)
            self.analyzer.roi_bg = None
        except AttributeError:
            pass

    def set_imageview(self, imageview):
        if imageview is not self.imageview:
            self.disable()
            self.analyzer.imageview = imageview
            self.toggle_enable()

    def create_roi(self, pen='w'):
        roi = pg.RectROI((200, 200), (200, 200), pen=pen)
        roi.addScaleHandle([1, 1], [0, 0])
        roi.addScaleHandle([0, 0], [1, 1])
        self.analyzer.imageview.addItem(roi)
        return roi

    def toggle_enable(self):
        if self.enable_checkBox.isChecked():
            self.plothistorywindow.show()
            self.enable()
        elif not self.enable_checkBox.isChecked():
            self.plothistorywindow.close()
            self.disable()

    def toggle_bg_subtract(self):
        if self.bg_subtract_checkBox.isChecked():
            self.enable_bg_subtract()
        elif not self.bg_subtract_checkBox.isChecked():
            self.disable_bg_subtract()

    def window_closed(self):
        self.disable()
        self.enable_checkBox.setChecked(False)
