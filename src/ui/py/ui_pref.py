# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/ui/pref.ui'
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

class Ui_pref(object):
    def setupUi(self, pref):
        pref.setObjectName(_fromUtf8("pref"))
        pref.resize(543, 223)
        pref.setMinimumSize(QtCore.QSize(0, 0))
        pref.setMaximumSize(QtCore.QSize(543, 429))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/images/logo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        pref.setWindowIcon(icon)
        self.tabWidget = QtGui.QTabWidget(pref)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 521, 201))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.groupBox_11 = QtGui.QGroupBox(self.tab)
        self.groupBox_11.setGeometry(QtCore.QRect(10, 10, 501, 151))
        self.groupBox_11.setObjectName(_fromUtf8("groupBox_11"))
        self.path = QtGui.QLineEdit(self.groupBox_11)
        self.path.setGeometry(QtCore.QRect(10, 70, 391, 20))
        self.path.setText(_fromUtf8(""))
        self.path.setObjectName(_fromUtf8("path"))
        self.rename_lga_warning_2 = QtGui.QLabel(self.groupBox_11)
        self.rename_lga_warning_2.setGeometry(QtCore.QRect(10, 44, 171, 16))
        self.rename_lga_warning_2.setStyleSheet(_fromUtf8(""))
        self.rename_lga_warning_2.setObjectName(_fromUtf8("rename_lga_warning_2"))
        self.browse = QtGui.QPushButton(self.groupBox_11)
        self.browse.setGeometry(QtCore.QRect(410, 70, 75, 23))
        self.browse.setObjectName(_fromUtf8("browse"))
        self.saveBtn = QtGui.QPushButton(self.groupBox_11)
        self.saveBtn.setGeometry(QtCore.QRect(410, 110, 75, 23))
        self.saveBtn.setObjectName(_fromUtf8("saveBtn"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))

        self.retranslateUi(pref)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(pref)

    def retranslateUi(self, pref):
        pref.setWindowTitle(_translate("pref", "Preference", None))
        self.groupBox_11.setTitle(_translate("pref", "Storage options", None))
        self.path.setPlaceholderText(_translate("pref", "Paste path here or click browse to locate path", None))
        self.rename_lga_warning_2.setText(_translate("pref", "Where to save downloaded videos:", None))
        self.browse.setText(_translate("pref", "Browse path", None))
        self.saveBtn.setText(_translate("pref", "Save settings", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("pref", "Setup", None))

import resources_rc
