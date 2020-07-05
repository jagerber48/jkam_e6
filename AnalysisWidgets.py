import numpy as np
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
QtCore.Signal = QtCore.pyqtSignal
import pyqtgraph as pg


class IntegrateROI(QWidget):
	
	def __init__(self, subtract_bkg=False, num_history=200, parent=None):
		super(IntegrateROI, self).__init__(parent)
		self.subtract_bkg = subtract_bkg
		self.num_history = num_history

		self.history = np.zeros(self.num_history)
		
		self.history_min = self.history.min()
		self.history_max = self.history.max()
		self.roi = None
		
		layout = QVBoxLayout()

		self.history_widget = pg.PlotWidget(self)
		self.history_widget.disableAutoRange()
		self.history_plot = self.history_widget.plot()
		self.history_plot.setPen(width=2)	
		self.history_widget.setXRange(0, self.num_history)
		
		plot_item = self.history_widget.getPlotItem()
		plot_item.showGrid(x=True, y=True)
		plot_item.getAxis('bottom').setGrid(255)
		plot_item.getAxis('left').setGrid(255)		
		plot_item.setLabel('bottom', text='Frame')
		plot_item.setLabel('left', text='Fluorescent counts')
		
		# self.history_widget.setYRange(self.history_min, self.history_max)

		self.min_button = QPushButton('Set Background', self)
		self.clear_button = QPushButton('Clear History', self)
		self.max_button = QPushButton('Reset Max', self)

		self.min_button.clicked.connect(self.set_min)
		self.clear_button.clicked.connect(self.clear_history)
		self.max_button.clicked.connect(self.set_max)

		button_layout = QHBoxLayout()
		button_layout.addWidget(self.min_button)
		button_layout.addWidget(self.clear_button)
		button_layout.addWidget(self.max_button)     

		layout.addWidget(self.history_widget)
		layout.addLayout(button_layout)
		self.setLayout(layout)

	def setup_figure(self, im_widget):
		self.roi = pg.RectROI((200, 200), (200, 200))
		self.roi.addScaleHandle([1, 1], [0, 0])
		self.roi.addScaleHandle([0, 0], [1, 1])
		im_widget.addItem(self.roi)		
		
	def clear_history(self):
		self.history[:] = 0
		self.history_plot.setData(self.history)		
		
	def set_min(self):
		self.history_min = self.history.min()
		self.history_widget.setYRange(self.history_min, self.history_max)

	def set_max(self):
		self.history_max = self.history.max()
		self.history_widget.setYRange(self.history_min, self.history_max)
		
	def analyze(self, capture, image_item):

		data = capture.data.astype(float)
		data[data == np.inf] = np.nan
		data[data == -np.inf] = np.nan

		total = np.nansum(data)
		total_num = capture.data.size
		
		roi_data = self.roi.getArrayRegion(data, image_item)
		
		roi_total = np.nansum(roi_data)
		roi_num = roi_data.size
		
		if self.subtract_bkg:
			bkg = (total - roi_total) / (total_num - roi_num)
			roi_sig = roi_total - roi_num * bkg        
		else:
			roi_sig = roi_total
		
		self.history = np.roll(self.history, -1)
		self.history[-1] = roi_sig
		
		self.history_plot.setData(self.history)
		
		self.history_max = max(self.history_max, self.history.max())
		self.history_widget.setYRange(self.history_min, self.history_max)


class AbsorptionROI(QWidget):
	
	def __init__(self, cross_section, pixel_size, magnification=1, num_history=200, threshold=None, parent=None):
		super(AbsorptionROI, self).__init__(parent)
		self.cross_section = cross_section
		self.pixel_size = pixel_size
		self.magnification = magnification
		self.num_history = num_history
		self.threshold = threshold

		self.history = np.empty(self.num_history)
		self.history[:] = 0
		
		self.history_min = np.nanmin(self.history)
		self.history_max = np.nanmax(self.history)
		self.roi = None
		
		layout = QVBoxLayout()

		self.history_widget = pg.PlotWidget(self)
		self.history_widget.disableAutoRange()
		self.history_plot = self.history_widget.plot()
		self.history_plot.setPen(width=2)
		
		plot_item = self.history_widget.getPlotItem()
		plot_item.showGrid(x=True, y=True)
		plot_item.getAxis('bottom').setGrid(255)
		plot_item.getAxis('left').setGrid(255)		
		plot_item.setLabel('bottom', text='Frame')
		plot_item.setLabel('left', text='Atom #')
		
		self.history_widget.setXRange(0, self.num_history)
		
		# self.history_widget.setYRange(self.history_min, self.history_max)

		self.min_button = QPushButton('Set Background', self)
		self.clear_button = QPushButton('Clear History', self)
		self.max_button = QPushButton('Reset Max', self)

		self.min_button.clicked.connect(self.set_min)
		self.clear_button.clicked.connect(self.clear_history)
		self.max_button.clicked.connect(self.set_max)

		button_layout = QHBoxLayout()
		button_layout.addWidget(self.min_button)
		button_layout.addWidget(self.clear_button)
		button_layout.addWidget(self.max_button)         

		layout.addWidget(self.history_widget)
		layout.addLayout(button_layout)
		self.setLayout(layout)
		
	def setup_figure(self, im_widget):
		self.roi = pg.RectROI((300, 10), (40, 25))
		self.roi.addScaleHandle([1, 1], [0, 0])
		self.roi.addScaleHandle([0, 0], [1, 1])
		im_widget.addItem(self.roi)		
		
	def clear_history(self):
		self.history[:] = 0
		self.history_plot.setData(self.history)		
		
	def set_min(self):
		self.history_min = np.nanmin(self.history)
		if np.isfinite(self.history_min) and np.isfinite(self.history_max):
			self.history_widget.setYRange(self.history_min, self.history_max)

	def set_max(self):
		self.history_max = np.nanmax(self.history)		
		if np.isfinite(self.history_min) and np.isfinite(self.history_max):
			self.history_widget.setYRange(self.history_min, self.history_max)
		
	def analyze(self, capture, image_item):
		data = capture.data.astype(float)
		# data[data == np.inf] = np.nan
		# data[data == -np.inf] = np.nan

		if self.threshold is not None:
			mask = capture.ref < self.threshold
			data[mask] = np.nan

		trans_min = .01
		trans_max = 1.5
		data[data > trans_max] = trans_max
		data[data < trans_min] = trans_min
		data = -np.log(data)
	
		roi_data = self.roi.getArrayRegion(data, image_item)
		roi_total = np.nansum(roi_data)
		
		Na = roi_total/self.cross_section*(self.pixel_size/self.magnification)**2
		
		self.history = np.roll(self.history, -1)
		self.history[-1] = Na
		
		self.history_plot.setData(self.history)
		
		self.history_max = max(self.history_max, np.nanmax(self.history))
		if np.isfinite(self.history_min) and np.isfinite(self.history_max):
			self.history_widget.setYRange(self.history_min, self.history_max)
