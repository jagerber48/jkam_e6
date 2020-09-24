from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
import pyqtgraph as pg


class CamView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CamView, self).__init__(parent=parent)

        self.imageview = pg.ImageView(parent=self, view=pg.PlotItem())
        self.imageitem = self.imageview.getImageItem()
        self.label = QtWidgets.QLabel(self)
        self.label.setText('Pixel: ( , ) Value: (Not Implemented)')
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.label)
        self.verticalLayout.addWidget(self.imageview)

        self.imageview.ui.roiBtn.hide()
        self.imageview.ui.menuBtn.hide()

        self.v_line = pg.InfiniteLine(angle=90, movable=False)
        self.h_line = pg.InfiniteLine(angle=0, movable=False)
        self.imageview.addItem(self.v_line, ignoreBounds=True)
        self.imageview.addItem(self.h_line, ignoreBounds=True)

        self.imageitem.scene().sigMouseClicked.connect(self.mouse_moved)
        self.image_data = None
        self.show()

    def setImage(self, img, *args, **kwargs):
        self.imageview.setImage(img, *args, **kwargs)
        self.image_data = img

    def mouse_moved(self, evt):
        if not (evt.button() == 1 and evt.double() is True):
            return
        scene_pos = evt.scenePos()
        view_pos = self.imageitem.getViewBox().mapSceneToView(scene_pos)
        i, j = view_pos.y(), view_pos.x()

        self.label.setText("pixel: (%d, %d)  value: %g" % (i, j, 0.42))
        self.h_line.setPos(i)
        self.v_line.setPos(j)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    ex = CamView()
    app.exec_()
    sys.exit(app.exec_())
