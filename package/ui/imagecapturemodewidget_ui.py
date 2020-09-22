# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_resources\imagecapturemodewidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ImageCaptureModeWidget(object):
    def setupUi(self, ImageCaptureModeWidget):
        ImageCaptureModeWidget.setObjectName("ImageCaptureModeWidget")
        ImageCaptureModeWidget.resize(147, 128)
        self.gridLayout = QtWidgets.QGridLayout(ImageCaptureModeWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QtWidgets.QFrame(ImageCaptureModeWidget)
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.absorption_mode_radioButton = QtWidgets.QRadioButton(self.frame)
        self.absorption_mode_radioButton.setObjectName("absorption_mode_radioButton")
        self.image_capture_buttonGroup = QtWidgets.QButtonGroup(ImageCaptureModeWidget)
        self.image_capture_buttonGroup.setObjectName("image_capture_buttonGroup")
        self.image_capture_buttonGroup.addButton(self.absorption_mode_radioButton)
        self.gridLayout_2.addWidget(self.absorption_mode_radioButton, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.fluorescence_mode_radioButton = QtWidgets.QRadioButton(self.frame)
        self.fluorescence_mode_radioButton.setObjectName("fluorescence_mode_radioButton")
        self.image_capture_buttonGroup.addButton(self.fluorescence_mode_radioButton)
        self.gridLayout_2.addWidget(self.fluorescence_mode_radioButton, 2, 0, 1, 1)
        self.video_mode_radioButton = QtWidgets.QRadioButton(self.frame)
        self.video_mode_radioButton.setChecked(True)
        self.video_mode_radioButton.setObjectName("video_mode_radioButton")
        self.image_capture_buttonGroup.addButton(self.video_mode_radioButton)
        self.gridLayout_2.addWidget(self.video_mode_radioButton, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 1, 1, 1)

        self.retranslateUi(ImageCaptureModeWidget)
        QtCore.QMetaObject.connectSlotsByName(ImageCaptureModeWidget)

    def retranslateUi(self, ImageCaptureModeWidget):
        _translate = QtCore.QCoreApplication.translate
        ImageCaptureModeWidget.setWindowTitle(_translate("ImageCaptureModeWidget", "Form"))
        self.absorption_mode_radioButton.setText(_translate("ImageCaptureModeWidget", "Absorption"))
        self.label.setText(_translate("ImageCaptureModeWidget", "Image Capture Mode"))
        self.fluorescence_mode_radioButton.setText(_translate("ImageCaptureModeWidget", "Fluorescence"))
        self.video_mode_radioButton.setText(_translate("ImageCaptureModeWidget", "Video"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ImageCaptureModeWidget = QtWidgets.QWidget()
    ui = Ui_ImageCaptureModeWidget()
    ui.setupUi(ImageCaptureModeWidget)
    ImageCaptureModeWidget.show()
    sys.exit(app.exec_())
