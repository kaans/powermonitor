# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(695, 501)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setHandleWidth(2)
        self.splitter.setObjectName("splitter")
        self.frmLeft = QtWidgets.QFrame(self.splitter)
        self.frmLeft.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frmLeft.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frmLeft.setObjectName("frmLeft")
        self.formLayout_2 = QtWidgets.QFormLayout(self.frmLeft)
        self.formLayout_2.setContentsMargins(11, 11, 11, 11)
        self.formLayout_2.setSpacing(6)
        self.formLayout_2.setObjectName("formLayout_2")
        self.lblComPort = QtWidgets.QLabel(self.frmLeft)
        self.lblComPort.setObjectName("lblComPort")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.lblComPort)
        self.cmbComPort = QtWidgets.QComboBox(self.frmLeft)
        self.cmbComPort.setObjectName("cmbComPort")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.cmbComPort)
        self.label = QtWidgets.QLabel(self.frmLeft)
        self.label.setObjectName("label")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.frmRight = QtWidgets.QFrame(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frmRight.sizePolicy().hasHeightForWidth())
        self.frmRight.setSizePolicy(sizePolicy)
        self.frmRight.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frmRight.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frmRight.setObjectName("frmRight")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frmRight)
        self.verticalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.plotBV = PlotWidget(self.frmRight)
        self.plotBV.setObjectName("plotBV")
        self.verticalLayout_2.addWidget(self.plotBV)
        self.verticalLayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 695, 21))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Power Monitor 0.1"))
        self.lblComPort.setText(_translate("MainWindow", "COM Port"))
        self.label.setText(_translate("MainWindow", "TextLabel"))

from pyqtgraph import PlotWidget
