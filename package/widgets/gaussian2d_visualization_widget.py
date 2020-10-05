import numpy as np
from uncertainties import ufloat
from enum import Enum
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, QSpacerItem, QSizePolicy
import pyqtgraph as pg

pg.setConfigOptions(imageAxisOrder='row-major')


class SliceAxisType(Enum):
    VERTICAL = 0
    HORIZONTAL = 1


class GaussianIntegrateAxisPlot(pg.PlotItem):
    def __init__(self, *args, **kwargs):
        super(GaussianIntegrateAxisPlot, self).__init__(*args, **kwargs)
        self.setMouseEnabled(x=False, y=False)

    def update(self, data_img, model_img, slice_axis, sx, sy, offset=0):
        """
        Integrate data along 1 axis of data_img and model_img and plot result.
        For horizontal slice integrate along vertical axis and flip y-axis to put slice plot underneath image in
        display.
        for vertical slice integrate along horizontal axis and plot the data vertically to put slice plot to the side
        of image in display.
        """
        self.clear()
        if slice_axis == SliceAxisType.VERTICAL:
            y_range = data_img.shape[0]
            integrate_axis = 1
            data_cut_data = np.sum(data_img, axis=integrate_axis) / np.sqrt(2 * np.pi * sx ** 2)
            model_cut_data = np.sum(model_img, axis=integrate_axis) / np.sqrt(2 * np.pi * sx ** 2)
            self.plot(data_cut_data, offset + np.arange(y_range),
                      pen=pg.mkPen(width=0.5), symbolBrush='w', symbolSize=5)
            self.plot(model_cut_data, offset + np.arange(y_range), pen=pg.mkPen('r'))

        elif slice_axis == SliceAxisType.HORIZONTAL:
            x_range = data_img.shape[1]
            integrate_axis = 0
            data_cut_data = np.sum(data_img, axis=integrate_axis) / np.sqrt(2 * np.pi * sy ** 2)
            model_cut_data = np.sum(model_img, axis=integrate_axis) / np.sqrt(2 * np.pi * sy ** 2)
            self.plot(offset + np.arange(x_range), data_cut_data,
                      pen=pg.mkPen(width=0.5), symbolBrush='w', symbolSize=5)
            self.plot(offset + np.arange(x_range), model_cut_data, pen=pg.mkPen('b'))
            self.invertY(True)


class Gaussian2DPlot(pg.PlotItem):
    def __init__(self, *args, **kwargs):
        super(Gaussian2DPlot, self).__init__(*args, **kwargs)
        self.image_item = pg.ImageItem()
        self.addItem(self.image_item)
        self.setAspectLocked(True, 1)

        self.v_line = pg.InfiniteLine(0, angle=90, movable=False, pen='r')
        self.addItem(self.v_line)
        self.h_line = pg.InfiniteLine(0, angle=0, movable=False, pen='b')
        self.addItem(self.h_line)
        self.x_line = pg.InfiniteLine((0, 0), angle=0, movable=False, pen='g')
        self.addItem(self.x_line)
        self.y_line = pg.InfiniteLine((0, 0), angle=90, movable=False, pen='y')
        self.addItem(self.y_line)

    def update(self, img, x0, y0, angle, x_offset=0, y_offset=0):
        self.image_item.setImage(img)
        self.image_item.setPos(x_offset, y_offset)
        self.v_line.setPos((x0, y0))
        self.h_line.setPos((x0, y0))
        self.x_line.setPos((x0, y0))
        self.x_line.setAngle(angle)
        self.y_line.setPos((x0, y0))
        self.y_line.setAngle(angle + 90)


class FitVisualizationWindow(QWidget):
    window_close_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(FitVisualizationWindow, self).__init__(parent=parent)
        self.fit_struct = None
        self.setupUi()
        self.setup_plots()

    def setupUi(self):
        self.resize(800, 800)
        self.gridLayout = QGridLayout(self)
        self.pgGraphicsLayout = pg.GraphicsLayoutWidget(parent=self)
        self.pgGraphicsLayout.show()
        self.text_display_verticalLayout = QVBoxLayout(self)
        self.gridLayout.addWidget(self.pgGraphicsLayout, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.text_display_verticalLayout, 0, 1, 1, 1)

    def setup_plots(self):
        self.data_plot = Gaussian2DPlot()
        self.pgGraphicsLayout.addItem(self.data_plot, 0, 0, 1, 1)
        self.data_plot.getViewBox().invertY()

        self.model_plot = Gaussian2DPlot()
        self.pgGraphicsLayout.addItem(self.model_plot, 1, 1, 1, 1)
        self.model_plot.getViewBox().invertY()

        self.model_plot.setXLink(self.data_plot.getViewBox())
        self.model_plot.setYLink(self.data_plot.getViewBox())

        self.horizontal_cut_plot = GaussianIntegrateAxisPlot()
        self.pgGraphicsLayout.addItem(self.horizontal_cut_plot, 1, 0, 1, 1)
        self.horizontal_cut_plot.setXLink(self.data_plot.getViewBox())

        self.vertical_cut_plot = GaussianIntegrateAxisPlot()
        self.pgGraphicsLayout.addItem(self.vertical_cut_plot, 0, 1, 1, 1)
        self.vertical_cut_plot.setYLink(self.data_plot.getViewBox())
        self.vertical_cut_plot.getViewBox().invertY()

    def update_text_display(self):
        clearLayout(self.text_display_verticalLayout)

        self.text_display_verticalLayout.addItem(QSpacerItem(14, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        for key in self.fit_struct['param_keys']:
            label = QLabel()
            val = round(self.fit_struct[key]['val'], 3)
            std = round(self.fit_struct[key]['std'], 3)
            val_str = ufloat(val, std)
            label.setText(f'{str(key)} = {val_str}')
            self.text_display_verticalLayout.addWidget(label)
        self.text_display_verticalLayout.addItem(QSpacerItem(14, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def update(self, fit_struct=None, x_offset=0, y_offset=0):
        if fit_struct is not None:
            self.fit_struct = fit_struct
        x0 = self.fit_struct['x0']['val'] + x_offset
        y0 = self.fit_struct['y0']['val'] + y_offset
        sx = self.fit_struct['sx']['val']
        sy = self.fit_struct['sy']['val']
        angle = self.fit_struct['angle']['val']
        data_img = self.fit_struct['data_img']
        model_img = self.fit_struct['model_img']
        self.data_plot.update(data_img, x0, y0, angle, x_offset=x_offset, y_offset=y_offset)
        self.model_plot.update(model_img, x0, y0, angle, x_offset=x_offset, y_offset=y_offset)
        self.horizontal_cut_plot.update(data_img, model_img, slice_axis=SliceAxisType.HORIZONTAL,
                                        sx=sx, sy=sy, offset=x_offset)
        self.vertical_cut_plot.update(data_img, model_img, slice_axis=SliceAxisType.VERTICAL,
                                      sx=sx, sy=sy, offset=y_offset)
        self.data_plot.autoRange()
        self.update_text_display()

    def closeEvent(self, event):
        self.window_close_signal.emit()
        return super().closeEvent(event)


def clearLayout(layout):
  while layout.count():
    child = layout.takeAt(0)
    if child.widget():
      child.widget().deleteLater()