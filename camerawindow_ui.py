# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'camerawindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CameraWindow(object):
    def setupUi(self, CameraWindow):
        CameraWindow.setObjectName("CameraWindow")
        CameraWindow.resize(622, 625)
        self.centralwidget = QtWidgets.QWidget(CameraWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.imageview_widget = ImageView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.imageview_widget.sizePolicy().hasHeightForWidth())
        self.imageview_widget.setSizePolicy(sizePolicy)
        self.imageview_widget.setMinimumSize(QtCore.QSize(400, 400))
        self.imageview_widget.setObjectName("imageview_widget")
        self.gridLayout.addWidget(self.imageview_widget, 0, 0, 1, 1)
        self.history_widget = IntegrateROI(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.history_widget.sizePolicy().hasHeightForWidth())
        self.history_widget.setSizePolicy(sizePolicy)
        self.history_widget.setMinimumSize(QtCore.QSize(0, 150))
        self.history_widget.setObjectName("history_widget")
        self.gridLayout.addWidget(self.history_widget, 2, 0, 1, 2)
        self.settings_verticalLayout = QtWidgets.QVBoxLayout()
        self.settings_verticalLayout.setObjectName("settings_verticalLayout")
        self.arm_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.arm_pushButton.setCheckable(True)
        self.arm_pushButton.setObjectName("arm_pushButton")
        self.settings_verticalLayout.addWidget(self.arm_pushButton)
        self.start_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.start_pushButton.setEnabled(False)
        self.start_pushButton.setCheckable(True)
        self.start_pushButton.setObjectName("start_pushButton")
        self.settings_verticalLayout.addWidget(self.start_pushButton)
        self.serial_label = QtWidgets.QLabel(self.centralwidget)
        self.serial_label.setObjectName("serial_label")
        self.settings_verticalLayout.addWidget(self.serial_label)
        self.exposure_formLayout = QtWidgets.QFormLayout()
        self.exposure_formLayout.setObjectName("exposure_formLayout")
        self.exposure_label = QtWidgets.QLabel(self.centralwidget)
        self.exposure_label.setObjectName("exposure_label")
        self.exposure_formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.exposure_label)
        self.exposure_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.exposure_lineEdit.setMaximumSize(QtCore.QSize(60, 16777215))
        self.exposure_lineEdit.setObjectName("exposure_lineEdit")
        self.exposure_formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.exposure_lineEdit)
        self.settings_verticalLayout.addLayout(self.exposure_formLayout)
        self.exposure_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.exposure_pushButton.setObjectName("exposure_pushButton")
        self.settings_verticalLayout.addWidget(self.exposure_pushButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.settings_verticalLayout.addItem(spacerItem)
        self.gaussfit_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.gaussfit_pushButton.setObjectName("gaussfit_pushButton")
        self.settings_verticalLayout.addWidget(self.gaussfit_pushButton)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.settings_verticalLayout.addItem(spacerItem1)
        self.autoscale_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.autoscale_pushButton.setObjectName("autoscale_pushButton")
        self.settings_verticalLayout.addWidget(self.autoscale_pushButton)
        self.fullscale_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.fullscale_pushButton.setObjectName("fullscale_pushButton")
        self.settings_verticalLayout.addWidget(self.fullscale_pushButton)
        self.customscale_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.customscale_pushButton.setObjectName("customscale_pushButton")
        self.settings_verticalLayout.addWidget(self.customscale_pushButton)
        self.plot_formLayout = QtWidgets.QFormLayout()
        self.plot_formLayout.setObjectName("plot_formLayout")
        self.max_label = QtWidgets.QLabel(self.centralwidget)
        self.max_label.setObjectName("max_label")
        self.plot_formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.max_label)
        self.max_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.max_lineEdit.setMaximumSize(QtCore.QSize(50, 16777215))
        self.max_lineEdit.setObjectName("max_lineEdit")
        self.plot_formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.max_lineEdit)
        self.min_label = QtWidgets.QLabel(self.centralwidget)
        self.min_label.setObjectName("min_label")
        self.plot_formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.min_label)
        self.min_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.min_lineEdit.setMaximumSize(QtCore.QSize(50, 16777215))
        self.min_lineEdit.setObjectName("min_lineEdit")
        self.plot_formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.min_lineEdit)
        self.cmap_label = QtWidgets.QLabel(self.centralwidget)
        self.cmap_label.setObjectName("cmap_label")
        self.plot_formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.cmap_label)
        self.cmap_comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.cmap_comboBox.setObjectName("cmap_comboBox")
        self.cmap_comboBox.addItem("")
        self.cmap_comboBox.addItem("")
        self.cmap_comboBox.addItem("")
        self.cmap_comboBox.addItem("")
        self.plot_formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.cmap_comboBox)
        self.settings_verticalLayout.addLayout(self.plot_formLayout)
        self.gridLayout.addLayout(self.settings_verticalLayout, 0, 1, 1, 1)
        CameraWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(CameraWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 622, 26))
        self.menubar.setObjectName("menubar")
        CameraWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(CameraWindow)
        self.statusbar.setObjectName("statusbar")
        CameraWindow.setStatusBar(self.statusbar)

        self.retranslateUi(CameraWindow)
        QtCore.QMetaObject.connectSlotsByName(CameraWindow)

    def retranslateUi(self, CameraWindow):
        _translate = QtCore.QCoreApplication.translate
        CameraWindow.setWindowTitle(_translate("CameraWindow", "jkam"))
        self.arm_pushButton.setText(_translate("CameraWindow", "Arm Camera"))
        self.start_pushButton.setText(_translate("CameraWindow", "Start Camera"))
        self.serial_label.setText(_translate("CameraWindow", "Serial Number: xxxxxxxx"))
        self.exposure_label.setText(_translate("CameraWindow", "Exposure Time (ms):"))
        self.exposure_lineEdit.setText(_translate("CameraWindow", "10"))
        self.exposure_pushButton.setText(_translate("CameraWindow", "Update Exposure"))
        self.gaussfit_pushButton.setText(_translate("CameraWindow", "Gaussian Fit"))
        self.autoscale_pushButton.setText(_translate("CameraWindow", "Auto Scale"))
        self.fullscale_pushButton.setText(_translate("CameraWindow", "Full Scale"))
        self.customscale_pushButton.setText(_translate("CameraWindow", "Custom Scale"))
        self.max_label.setText(_translate("CameraWindow", "Max"))
        self.max_lineEdit.setText(_translate("CameraWindow", "0"))
        self.min_label.setText(_translate("CameraWindow", "Min"))
        self.min_lineEdit.setText(_translate("CameraWindow", "255"))
        self.cmap_label.setText(_translate("CameraWindow", "Color Map"))
        self.cmap_comboBox.setItemText(0, _translate("CameraWindow", "jet"))
        self.cmap_comboBox.setItemText(1, _translate("CameraWindow", "gray"))
        self.cmap_comboBox.setItemText(2, _translate("CameraWindow", "viridis"))
        self.cmap_comboBox.setItemText(3, _translate("CameraWindow", "false2"))
from AnalysisWidgets import IntegrateROI
from pyqtgraph import ImageView


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CameraWindow = QtWidgets.QMainWindow()
    ui = Ui_CameraWindow()
    ui.setupUi(CameraWindow)
    CameraWindow.show()
    sys.exit(app.exec_())
