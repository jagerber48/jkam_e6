# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'absorption_view_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AbsorptionViewWidget(object):
    def setupUi(self, AbsorptionViewWidget):
        AbsorptionViewWidget.setObjectName("AbsorptionViewWidget")
        AbsorptionViewWidget.resize(615, 493)
        self.gridLayout = QtWidgets.QGridLayout(AbsorptionViewWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(AbsorptionViewWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.N_tab = QtWidgets.QWidget()
        self.N_tab.setObjectName("N_tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.N_tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.N_view_editor = ImageViewEditor(self.N_tab)
        self.N_view_editor.setObjectName("N_view_editor")
        self.gridLayout_2.addWidget(self.N_view_editor, 0, 0, 1, 1)
        self.tabWidget.addTab(self.N_tab, "")
        self.OD_tab = QtWidgets.QWidget()
        self.OD_tab.setObjectName("OD_tab")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.OD_tab)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.OD_view_editor = ImageViewEditor(self.OD_tab)
        self.OD_view_editor.setObjectName("OD_view_editor")
        self.gridLayout_3.addWidget(self.OD_view_editor, 0, 0, 1, 1)
        self.tabWidget.addTab(self.OD_tab, "")
        self.atom_tab = QtWidgets.QWidget()
        self.atom_tab.setObjectName("atom_tab")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.atom_tab)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.atom_view_editor = ImageViewEditor(self.atom_tab)
        self.atom_view_editor.setObjectName("atom_view_editor")
        self.gridLayout_4.addWidget(self.atom_view_editor, 0, 0, 1, 1)
        self.tabWidget.addTab(self.atom_tab, "")
        self.bright_tab = QtWidgets.QWidget()
        self.bright_tab.setObjectName("bright_tab")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.bright_tab)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.bright_view_editor = ImageViewEditor(self.bright_tab)
        self.bright_view_editor.setObjectName("bright_view_editor")
        self.gridLayout_6.addWidget(self.bright_view_editor, 0, 0, 1, 1)
        self.tabWidget.addTab(self.bright_tab, "")
        self.dark_tab = QtWidgets.QWidget()
        self.dark_tab.setObjectName("dark_tab")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.dark_tab)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.dark_view_editor = ImageViewEditor(self.dark_tab)
        self.dark_view_editor.setObjectName("dark_view_editor")
        self.gridLayout_5.addWidget(self.dark_view_editor, 0, 0, 1, 1)
        self.tabWidget.addTab(self.dark_tab, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(AbsorptionViewWidget)
        self.tabWidget.setCurrentIndex(4)
        QtCore.QMetaObject.connectSlotsByName(AbsorptionViewWidget)

    def retranslateUi(self, AbsorptionViewWidget):
        _translate = QtCore.QCoreApplication.translate
        AbsorptionViewWidget.setWindowTitle(_translate("AbsorptionViewWidget", "Form"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.N_tab), _translate("AbsorptionViewWidget", "Atom Number"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.OD_tab), _translate("AbsorptionViewWidget", "Optical Density"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.atom_tab), _translate("AbsorptionViewWidget", "With Atoms Image"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.bright_tab), _translate("AbsorptionViewWidget", "Bright Image"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.dark_tab), _translate("AbsorptionViewWidget", "Dark Image"))
from imagevieweditor import ImageViewEditor


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    AbsorptionViewWidget = QtWidgets.QWidget()
    ui = Ui_AbsorptionViewWidget()
    ui.setupUi(AbsorptionViewWidget)
    AbsorptionViewWidget.show()
    sys.exit(app.exec_())
