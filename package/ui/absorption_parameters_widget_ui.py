# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_resources\absorption_parameters_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AbsorptionParametersWidget(object):
    def setupUi(self, AbsorptionParametersWidget):
        AbsorptionParametersWidget.setObjectName("AbsorptionParametersWidget")
        AbsorptionParametersWidget.resize(291, 472)
        self.gridLayout = QtWidgets.QGridLayout(AbsorptionParametersWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.line = QtWidgets.QFrame(AbsorptionParametersWidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 1, 0, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.close_pushButton = QtWidgets.QPushButton(AbsorptionParametersWidget)
        self.close_pushButton.setObjectName("close_pushButton")
        self.horizontalLayout.addWidget(self.close_pushButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.gridLayout.addLayout(self.horizontalLayout, 17, 0, 1, 2)
        self.line_2 = QtWidgets.QFrame(AbsorptionParametersWidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 5, 0, 1, 2)
        self.title_label = QtWidgets.QLabel(AbsorptionParametersWidget)
        self.title_label.setObjectName("title_label")
        self.gridLayout.addWidget(self.title_label, 0, 0, 1, 2)
        self.line_3 = QtWidgets.QFrame(AbsorptionParametersWidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 10, 0, 1, 2)
        self.system_frame = QtWidgets.QFrame(AbsorptionParametersWidget)
        self.system_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.system_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.system_frame.setObjectName("system_frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.system_frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.system_value_label = QtWidgets.QLabel(self.system_frame)
        self.system_value_label.setObjectName("system_value_label")
        self.gridLayout_2.addWidget(self.system_value_label, 0, 1, 1, 1)
        self.system_label = QtWidgets.QLabel(self.system_frame)
        self.system_label.setObjectName("system_label")
        self.gridLayout_2.addWidget(self.system_label, 0, 0, 1, 1)
        self.pixel_value_label = QtWidgets.QLabel(self.system_frame)
        self.pixel_value_label.setObjectName("pixel_value_label")
        self.gridLayout_2.addWidget(self.pixel_value_label, 1, 1, 1, 1)
        self.pixel_label = QtWidgets.QLabel(self.system_frame)
        self.pixel_label.setObjectName("pixel_label")
        self.gridLayout_2.addWidget(self.pixel_label, 1, 0, 1, 1)
        self.magnification_label = QtWidgets.QLabel(self.system_frame)
        self.magnification_label.setObjectName("magnification_label")
        self.gridLayout_2.addWidget(self.magnification_label, 2, 0, 1, 1)
        self.magnification_value_label = QtWidgets.QLabel(self.system_frame)
        self.magnification_value_label.setObjectName("magnification_value_label")
        self.gridLayout_2.addWidget(self.magnification_value_label, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.system_frame, 6, 0, 1, 2)
        self.optical_frame = QtWidgets.QFrame(AbsorptionParametersWidget)
        self.optical_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.optical_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.optical_frame.setObjectName("optical_frame")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.optical_frame)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.optical_label = QtWidgets.QLabel(self.optical_frame)
        self.optical_label.setObjectName("optical_label")
        self.gridLayout_3.addWidget(self.optical_label, 0, 0, 1, 2)
        self.pulse_label = QtWidgets.QLabel(self.optical_frame)
        self.pulse_label.setObjectName("pulse_label")
        self.gridLayout_3.addWidget(self.pulse_label, 1, 0, 1, 1)
        self.pulse_value_label = QtWidgets.QLabel(self.optical_frame)
        self.pulse_value_label.setText("")
        self.pulse_value_label.setObjectName("pulse_value_label")
        self.gridLayout_3.addWidget(self.pulse_value_label, 1, 1, 1, 1)
        self.detuning_label = QtWidgets.QLabel(self.optical_frame)
        self.detuning_label.setObjectName("detuning_label")
        self.gridLayout_3.addWidget(self.detuning_label, 2, 0, 1, 1)
        self.detuning_value_label = QtWidgets.QLabel(self.optical_frame)
        self.detuning_value_label.setText("")
        self.detuning_value_label.setObjectName("detuning_value_label")
        self.gridLayout_3.addWidget(self.detuning_value_label, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.optical_frame, 2, 0, 1, 2)
        self.atom_frame = QtWidgets.QFrame(AbsorptionParametersWidget)
        self.atom_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.atom_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.atom_frame.setObjectName("atom_frame")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.atom_frame)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.atom_value_label = QtWidgets.QLabel(self.atom_frame)
        self.atom_value_label.setObjectName("atom_value_label")
        self.gridLayout_4.addWidget(self.atom_value_label, 0, 1, 1, 1)
        self.frequency_label = QtWidgets.QLabel(self.atom_frame)
        self.frequency_label.setObjectName("frequency_label")
        self.gridLayout_4.addWidget(self.frequency_label, 1, 0, 1, 1)
        self.isat_label = QtWidgets.QLabel(self.atom_frame)
        self.isat_label.setObjectName("isat_label")
        self.gridLayout_4.addWidget(self.isat_label, 3, 0, 1, 1)
        self.atom_label = QtWidgets.QLabel(self.atom_frame)
        self.atom_label.setObjectName("atom_label")
        self.gridLayout_4.addWidget(self.atom_label, 0, 0, 1, 1)
        self.cross_section_label = QtWidgets.QLabel(self.atom_frame)
        self.cross_section_label.setObjectName("cross_section_label")
        self.gridLayout_4.addWidget(self.cross_section_label, 2, 0, 1, 1)
        self.linewidth_label = QtWidgets.QLabel(self.atom_frame)
        self.linewidth_label.setObjectName("linewidth_label")
        self.gridLayout_4.addWidget(self.linewidth_label, 4, 0, 1, 1)
        self.frequency_value_label = QtWidgets.QLabel(self.atom_frame)
        self.frequency_value_label.setObjectName("frequency_value_label")
        self.gridLayout_4.addWidget(self.frequency_value_label, 1, 1, 1, 1)
        self.cross_section_value_label = QtWidgets.QLabel(self.atom_frame)
        self.cross_section_value_label.setObjectName("cross_section_value_label")
        self.gridLayout_4.addWidget(self.cross_section_value_label, 2, 1, 1, 1)
        self.isat_value_label = QtWidgets.QLabel(self.atom_frame)
        self.isat_value_label.setObjectName("isat_value_label")
        self.gridLayout_4.addWidget(self.isat_value_label, 3, 1, 1, 1)
        self.linewidth_value_label = QtWidgets.QLabel(self.atom_frame)
        self.linewidth_value_label.setObjectName("linewidth_value_label")
        self.gridLayout_4.addWidget(self.linewidth_value_label, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.atom_frame, 12, 0, 1, 2)

        self.retranslateUi(AbsorptionParametersWidget)
        QtCore.QMetaObject.connectSlotsByName(AbsorptionParametersWidget)

    def retranslateUi(self, AbsorptionParametersWidget):
        _translate = QtCore.QCoreApplication.translate
        AbsorptionParametersWidget.setWindowTitle(_translate("AbsorptionParametersWidget", "Form"))
        self.close_pushButton.setText(_translate("AbsorptionParametersWidget", "Close"))
        self.title_label.setText(_translate("AbsorptionParametersWidget", "Absorption Imaging Parameters:"))
        self.system_value_label.setText(_translate("AbsorptionParametersWidget", "System"))
        self.system_label.setText(_translate("AbsorptionParametersWidget", "Imaging System:"))
        self.pixel_value_label.setText(_translate("AbsorptionParametersWidget", "5 um"))
        self.pixel_label.setText(_translate("AbsorptionParametersWidget", "Pixel Size:"))
        self.magnification_label.setText(_translate("AbsorptionParametersWidget", "Magnification:"))
        self.magnification_value_label.setText(_translate("AbsorptionParametersWidget", "1"))
        self.optical_label.setText(_translate("AbsorptionParametersWidget", "Optical Conditions:"))
        self.pulse_label.setText(_translate("AbsorptionParametersWidget", "Pulse Time:"))
        self.detuning_label.setText(_translate("AbsorptionParametersWidget", "Detuning:"))
        self.atom_value_label.setText(_translate("AbsorptionParametersWidget", "Rb"))
        self.frequency_label.setText(_translate("AbsorptionParametersWidget", "Transition Frequency"))
        self.isat_label.setText(_translate("AbsorptionParametersWidget", "Saturation Intensity:"))
        self.atom_label.setText(_translate("AbsorptionParametersWidget", "Atom:"))
        self.cross_section_label.setText(_translate("AbsorptionParametersWidget", "Scattering Cross Section:"))
        self.linewidth_label.setText(_translate("AbsorptionParametersWidget", "Linewidth (FWHM):"))
        self.frequency_value_label.setText(_translate("AbsorptionParametersWidget", "384 THz"))
        self.cross_section_value_label.setText(_translate("AbsorptionParametersWidget", "cm<sup>2</sup>"))
        self.isat_value_label.setText(_translate("AbsorptionParametersWidget", "mW/cm<sup>2</sup>"))
        self.linewidth_value_label.setText(_translate("AbsorptionParametersWidget", "6 MHz"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    AbsorptionParametersWidget = QtWidgets.QWidget()
    ui = Ui_AbsorptionParametersWidget()
    ui.setupUi(AbsorptionParametersWidget)
    AbsorptionParametersWidget.show()
    sys.exit(app.exec_())
