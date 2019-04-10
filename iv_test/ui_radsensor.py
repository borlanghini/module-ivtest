# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rad_sensor.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_SetupRadSensDlg(object):
    def setupUi(self, SetupRadSensDlg):
        SetupRadSensDlg.setObjectName(_fromUtf8("SetupRadSensDlg"))
        SetupRadSensDlg.resize(422, 300)
        self.buttonBox = QtGui.QDialogButtonBox(SetupRadSensDlg)
        self.buttonBox.setGeometry(QtCore.QRect(340, 10, 81, 241))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.testmeasurement = QtGui.QPushButton(SetupRadSensDlg)
        self.testmeasurement.setGeometry(QtCore.QRect(20, 170, 100, 26))
        self.testmeasurement.setObjectName(_fromUtf8("testmeasurement"))
        self.radLcdNumber = QtGui.QLCDNumber(SetupRadSensDlg)
        self.radLcdNumber.setGeometry(QtCore.QRect(140, 166, 101, 31))
        self.radLcdNumber.setFrameShape(QtGui.QFrame.StyledPanel)
        self.radLcdNumber.setFrameShadow(QtGui.QFrame.Raised)
        self.radLcdNumber.setSmallDecimalPoint(True)
        self.radLcdNumber.setDigitCount(5)
        self.radLcdNumber.setObjectName(_fromUtf8("radLcdNumber"))
        self.label_2 = QtGui.QLabel(SetupRadSensDlg)
        self.label_2.setGeometry(QtCore.QRect(250, 170, 67, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.splitter = QtGui.QSplitter(SetupRadSensDlg)
        self.splitter.setGeometry(QtCore.QRect(16, 57, 261, 33))
        self.splitter.setMinimumSize(QtCore.QSize(261, 33))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.label = QtGui.QLabel(self.splitter)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setObjectName(_fromUtf8("label"))
        self.calspinBox = QtGui.QSpinBox(self.splitter)
        self.calspinBox.setMinimumSize(QtCore.QSize(89, 33))
        self.calspinBox.setMaximum(300)
        self.calspinBox.setObjectName(_fromUtf8("calspinBox"))

        self.retranslateUi(SetupRadSensDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SetupRadSensDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SetupRadSensDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(SetupRadSensDlg)

    def retranslateUi(self, SetupRadSensDlg):
        SetupRadSensDlg.setWindowTitle(_translate("SetupRadSensDlg", "Dialog", None))
        self.testmeasurement.setText(_translate("SetupRadSensDlg", "Measure", None))
        self.label_2.setText(_translate("SetupRadSensDlg", "<html><head/><body><p><span style=\" font-weight:600;\">W/m</span><span style=\" font-weight:600; vertical-align:super;\">2</span></p></body></html>", None))
        self.label.setText(_translate("SetupRadSensDlg", "Voltage value for 1 Sun", None))
        self.calspinBox.setSuffix(_translate("SetupRadSensDlg", " mV", None))

