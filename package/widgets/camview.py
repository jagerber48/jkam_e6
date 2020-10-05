from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
import pyqtgraph as pg

pg.setConfigOptions(imageAxisOrder='row-major')


class CamView(QtWidgets.QWidget):
    crosshair_moved_signal = pyqtSignal(object)

    def __init__(self, parent=None):
        super(CamView, self).__init__(parent=parent)

        self.imageview = pg.ImageView(parent=self, view=pg.PlotItem())
        self.imageitem = self.imageview.getImageItem()
        self.label = QtWidgets.QLabel(self)
        self.label.setText('Pixel: ( , ) Value: None')
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.label)
        self.verticalLayout.addWidget(self.imageview)

        self.imageview.ui.roiBtn.hide()
        self.imageview.ui.menuBtn.hide()

        self.v_line = pg.InfiniteLine(angle=90, movable=False)
        self.h_line = pg.InfiniteLine(angle=0, movable=False)
        self.imageview.addItem(self.v_line, ignoreBounds=True)
        self.imageview.addItem(self.h_line, ignoreBounds=True)
        self.crosshair_x = 0
        self.crosshair_y = 0

        self.imageitem.scene().sigMouseClicked.connect(self.mouse_moved)
        self.image_data = None
        self.show()

    def setImage(self, img, *args, **kwargs):
        self.imageview.setImage(img, *args, **kwargs)
        self.image_data = img
        self.set_crosshair(self.crosshair_x, self.crosshair_y)

    def mouse_moved(self, evt, signal=True):
        """
        Capture mouse click event and center curson on the pixel where the mouse clicked. scene_pos seems to be
        returned in column major order. That is,
        1st coordinate is horizontal (column) index (x) and
        2nd coordinate is vertical (row) index (y)
        """
        if not (evt.button() == 1 and evt.double() is True):
            return
        scene_pos = evt.scenePos()
        view_pos = self.imageitem.getViewBox().mapSceneToView(scene_pos)
        self.crosshair_x, self.crosshair_y = int(view_pos.x()), int(view_pos.y())
        self.set_crosshair(self.crosshair_x, self.crosshair_y)
        if signal:
            self.crosshair_moved_signal.emit(evt)

    def set_crosshair(self, x, y):
        """
        set crosshair to position x, y
        Here the arrays use row major order:
        1st index is vertical (row) index (x) and
        2nd index is horizontal (column) index (y)
        """
        x = int(x)
        y = int(y)
        pixel_text = f'Pixel: ({y}, {x})'
        value_text = 'Value: None'
        if self.image_data is not None:
            image_data_xrange = self.image_data.shape[1]
            image_data_yrange = self.image_data.shape[0]
            if (0 <= x <= image_data_xrange) and (0 <= y <= image_data_yrange):
                value = self.image_data[y, x]
                value_text = f'Value: {value:.2f}'
        self.label.setText(f'{pixel_text} {value_text}')
        self.v_line.setPos(x + 0.5)
        self.h_line.setPos(y + 0.5)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    ex = CamView()
    app.exec_()
    sys.exit(app.exec_())
