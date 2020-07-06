import sys
import datetime
from pathlib import Path
import numpy as np

# from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal
import pyqtgraph as pg

from GrasshopperDriver import GrasshopperObject
from AnalysisWidgets import AbsorptionROI
from ScanWidget import ScanWidget

from false2 import cmap

dataRoot = Path('C:/', 'users', 'justin', 'desktop', 'working', 'data')
andorRoot = Path('C:/', 'users', 'justin', 'desktop', 'working', 'andor')


class GuppyWindow(QtWidgets.QMainWindow):
    captured = pyqtSignal()

    def __init__(self):
        super(GuppyWindow, self).__init__()
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.thread.start()

        self.cam = GrasshopperObject()
        self.levels = (0, 1)
        self.data = None
        self.sig = None
        self.ref = None
        self.bkg = None
        self.timestamp = datetime.datetime.now()

        self.setWindowTitle("Guppy TOF")
        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.resize(1024, 768)
        layout = QtWidgets.QVBoxLayout()

        self.im_tof = pg.ImageView(self)
        self.im_sig = pg.ImageView(self)
        self.im_ref = pg.ImageView(self)
        self.im_bkg = pg.ImageView(self)

        for imView in (self.im_tof, self.im_sig, self.im_ref, self.im_bkg):
            imView.ui.roiBtn.hide()
            imView.ui.menuBtn.hide()
            imView.setColorMap(cmap)

        self.im_tof.setLevels(.4, 1.1)
        self.im_histogram = self.im_tof.getHistogramWidget().item
        self.im_histogram.setHistogramRange(.4, 1.1)

        self.im_stack = QtWidgets.QTabWidget()
        self.im_stack.addTab(self.im_tof, "Normalized")
        self.im_stack.addTab(self.im_sig, "Signal")
        self.im_stack.addTab(self.im_ref, "Reference")
        self.im_stack.addTab(self.im_bkg, "Background")
        self.im_stack.setTabPosition(QtWidgets.QTabWidget.South)

        self.camera_button = QtWidgets.QPushButton('Start Camera')
        self.camera_button.setCheckable(True)
        self.camera_button.clicked.connect(self.toggle_camera)

        self.scan_widget = ScanWidget('guppy', dataRoot, andorRoot)
        self.history_widget = AbsorptionROI(cross_section=2.9e-9, pixel_size=1.46e-3, num_history=200)

        layout.addWidget(self.camera_button)
        layout.addWidget(self.im_stack)
        layout.addWidget(self.scan_widget)
        layout.addWidget(self.history_widget)
        self.centralWidget.setLayout(layout)

        self.init_figure()
        self.cam.captured.connect(self.on_capture)

    def closeEvent(self, event):
        self.cam.abort()
        self.cam.close()

    def init_figure(self):
        self.data = np.array([])
        self.history_widget.setup_figure(self.im_tof)

    def toggle_camera(self):
        if self.camera_button.isChecked():
            try:
                self.cam.start_frames(nFrames=3)
                self.camera_button.setText('Camera Running')
            except Exception:
                self.cam.abort()
                self.cam.close()
                self.camera_button.setChecked(False)
                raise
        else:
            self.cam.abort()
            self.cam.close()
            self.camera_button.setText('Start Camera')

    def set_levels(self):
        self.levels = (self.data.min(), self.data.max())
        self.im_tof.setLevels(min=self.levels[0], max=self.levels[1])
        self.im_histogram.setHistogramRange(self.levels[0], self.levels[1])

    def on_capture(self, images):
        self.sig = images[:, :, 0]
        self.ref = images[:, :, 1]
        self.bkg = images[:, :, 2]

        numerator = self.sig - self.bkg
        denominator = self.ref - self.bkg

        # Set output to nan when dividing by zero
        self.data = np.true_divide(numerator, denominator,
                                   out=np.nan * np.zeros_like(numerator), where=(denominator != 0))

        self.timestamp = datetime.datetime.now()

        self.process_figure()
        # self.cam.start_frames(nFrames=3)

    def process_figure(self):
        if self.data.size == 0:
            return

        print('setting TOF img')
        self.im_tof.setImage(np.fliplr(self.data), autoLevels=False, autoHistogramRange=False)
        print('setting sig img')
        self.im_sig.setImage(np.fliplr(self.sig))
        print('setting ref img')
        self.im_ref.setImage(np.fliplr(self.ref))
        print('setting bg img')
        self.im_bkg.setImage(np.fliplr(self.bkg))

        self.history_widget.analyze(self, self.im_tof.getImageItem())

        self.scan_widget.saveData(self, self.timestamp)

    # self.saveFig()

    def save_fig(self):
        filename = "guppy.png"
        image1 = Path(andorRoot, filename)
        self.im_tof.getImageItem().save(image1)


def main():
    # Start Qt event loop unless running in interactive mode.
    # try:
    #     import ctypes
    #     myappid = u'ultracold.jkam'  # arbitrary string
    #     ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    # except:
    #     pass

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QIcon('favicon.ico'))
    ex = GuppyWindow()
    ex.show()
    app.exec_()


if __name__ == '__main__':
    main()
