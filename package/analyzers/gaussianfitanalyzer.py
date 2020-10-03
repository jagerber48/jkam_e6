from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget
import pyqtgraph as pg
from package.ui.gaussianfitanalyzer_ui import Ui_GaussianFitAnalyzer
from package.analyzers.smart_gaussian2d_fit import fit_gaussian2d
from package.widgets.gaussian2d_visualization_widget import FitVisualizationWindow


class GaussianFitWorker(QThread):
    analysis_complete_signal = pyqtSignal(dict)

    def __init__(self):
        super(GaussianFitWorker, self).__init__()
        self.roi = None

    def run(self):
        roi_slice = self.roi.getArraySlice(self.imageview.image, self.imageview.getImageItem())[0]
        roi_data = self.imageview.image[roi_slice]
        fit_struct = fit_gaussian2d(roi_data)
        self.analysis_complete_signal.emit(fit_struct)


class GaussianFitAnalyzer(QWidget, Ui_GaussianFitAnalyzer):
    def __init__(self, parent=None):
        super(GaussianFitAnalyzer, self).__init__(parent=parent)
        self.setupUi(self)
        self.worker = GaussianFitWorker()
        self.imageview = None
        self.enabled = False
        self.roi = None
        self.enable_checkBox.clicked.connect(self.toggle_enable)
        self.gaussian_fit_window = FitVisualizationWindow()
        self.gaussian_fit_window.window_close_signal.connect(self.window_closed)
        self.worker.analysis_complete_signal.connect(lambda x: self.gaussian_fit_window.update(x))

    def analyze(self):
        if self.enabled:
            self.worker.start()

    def enable(self):
        self.enabled = True
        self.roi = self.create_roi(pen='w')
        self.worker.roi = self.roi

    def disable(self):
        self.enabled = False
        self.remove_roi()

    def create_roi(self, pen='w'):
        roi = pg.RectROI((0, 0), (50, 50), pen=pen)
        roi.addScaleHandle([1, 1], [0, 0])
        roi.addScaleHandle([0, 0], [1, 1])
        self.imageview.addItem(roi)
        return roi

    def remove_roi(self):
        try:
            self.imageview.removeItem(self.analyzer.roi)
            self.worker.roi = None
        except AttributeError:
            pass

    def toggle_enable(self):
        if self.enable_checkBox.isChecked():
            self.gaussian_fit_window.show()
            self.enable()
        elif not self.enable_checkBox.isChecked():
            self.gaussian_fit_window.close()
            self.disable()

    def set_imageview(self, imageview):
        if imageview is not self.imageview:
            self.disable()
            self.imageview = imageview
            self.worker.imageview = self.imageview
            self.toggle_enable()

    def window_closed(self):
        self.disable()
        self.enable_checkBox.setChecked(False)