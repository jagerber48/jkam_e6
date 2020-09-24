from PyQt5.QtWidgets import QWidget
import pyqtgraph as pg
from package.ui.imageview_editor_ui import Ui_ImageViewEditor
from package.imagedata.colormaps import cmap_dict


class ImageViewEditor(QWidget, Ui_ImageViewEditor):
    def __init__(self, parent=None):
        super(ImageViewEditor, self).__init__(parent=parent)
        self.setupUi(self)

        # self.imageview.ui.roiBtn.hide()
        # self.imageview.ui.menuBtn.hide()
        # v_line = pg.InfiniteLine(angle=90, movable=True)
        # h_line = pg.InfiniteLine(angle=0, movable=True)
        # self.imageview.addItem(v_line, ignoreBounds=True)
        # self.imageview.addItem(h_line, ignoreBounds=True)

        self.imageview = self.camview.imageview
        self.levels = (0, 255)
        self.read_levels()
        self.image_data = None

        self.histogram = self.imageview.getHistogramWidget().item
        self.histogram.setHistogramRange(self.levels[0], self.levels[1])
        self.histogram.setLevels(self.levels[0], self.levels[1])
        self.set_cmap()

        self.autoscale_pushButton.clicked.connect(self.set_autoscale)
        self.fullscale_pushButton.clicked.connect(self.set_fullscale)
        self.customscale_pushButton.clicked.connect(self.set_customscale)
        self.cmap_comboBox.activated.connect(self.set_cmap)

    def setImage(self, img, *args, **kwargs):
        self.camview.setImage(img, *args, **kwargs)
        self.image_data = img

    def read_levels(self):
        try:
            level_min = float(self.min_lineEdit.text())
            level_max = float(self.max_lineEdit.text())
            self.levels = (level_min, level_max)
        except ValueError:
            print('Invalid input for min or max scale')
            self.write_levels()

    def write_levels(self):
        self.min_lineEdit.setText(f'{self.levels[0]:.2f}')
        self.max_lineEdit.setText(f'{self.levels[1]:.2f}')

    def set_autoscale(self):
        self.imageview.autoLevels()
        self.levels = (self.imageview.levelMin, self.imageview.levelMax)
        self.write_levels()

    def set_fullscale(self):
        self.levels = [0, 255]
        self.imageview.setLevels(min=self.levels[0], max=self.levels[1])
        self.histogram.setHistogramRange(self.levels[0], self.levels[1])
        self.write_levels()

    def set_customscale(self):
        self.read_levels()
        self.imageview.setLevels(min=self.levels[0], max=self.levels[1])

    def set_cmap(self):
        cmap_name = self.cmap_comboBox.currentText().lower()
        cmap = cmap_dict[cmap_name]
        self.imageview.setColorMap(cmap)
        self.histogram.gradient.showTicks(False)
