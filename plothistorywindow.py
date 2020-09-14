import numpy as np
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal
from ui_components.plothistorywindow_ui import Ui_PlotHistoryWindow


class PlotHistoryWindow(QMainWindow, Ui_PlotHistoryWindow):
    """
    Rolling History Widget. pyqtgraph with the main functionality of providing a rolling history of data which has
    been loaded in through the "append_data" method.
    """
    window_close_signal = pyqtSignal()

    def __init__(self, label='counts', num_history=200):
        super(PlotHistoryWindow, self).__init__()
        self.setupUi(self)

        self.label = label
        self.num_history = num_history
        self.history = np.zeros(self.num_history)
        self.history_min = self.history.min()
        self.history_max = self.history.max()

        self.history_PlotWidget.disableAutoRange()
        self.history_plot = self.history_PlotWidget.plot()
        self.history_plot.setPen(width=2)
        self.history_PlotWidget.setXRange(0, self.num_history)

        plot_item = self.history_PlotWidget.getPlotItem()
        plot_item.showGrid(x=True, y=True)
        plot_item.getAxis('bottom').setGrid(255)
        plot_item.getAxis('left').setGrid(255)
        plot_item.setLabel('bottom', text='Frame')
        plot_item.setLabel('left', text=self.label)

        self.set_min_pushButton.clicked.connect(self.set_min)
        self.clear_pushButton.clicked.connect(self.clear_history)
        self.set_max_pushButton.clicked.connect(self.set_max)

    def append_data(self, data):
        self.history = np.roll(self.history, -1)
        self.history[-1] = data
        self.plot()
        self.data_label.setText(f'{data:.3e}')

    def clear_history(self):
        self.history[:] = 0
        self.plot()

    def set_min(self):
        self.history_min = self.history.min()
        self.history_PlotWidget.setYRange(self.history_min, self.history_max)

    def set_max(self):
        self.history_max = self.history.max()
        self.history_PlotWidget.setYRange(self.history_min, self.history_max)

    def plot(self):
        self.history_plot.setData(self.history)
        # self.history_PlotWidget.setYRange(self.history_min, self.history_max)

    def closeEvent(self, event):
        self.window_close_signal.emit()
        return super().closeEvent(event)
