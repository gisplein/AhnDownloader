# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'popup_dialog_base.ui'
#
# Created: Sat Jan 07 12:36:20 2017
#      by: PyQt4 UI code generator 4.10.2
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(450, 215)
        Dialog.setMinimumSize(QtCore.QSize(450, 215))
        Dialog.setMaximumSize(QtCore.QSize(450, 215))
        Dialog.setModal(True)
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 20, 46, 13))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(20, 50, 46, 13))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(20, 80, 46, 13))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(170, 80, 46, 13))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(20, 110, 46, 13))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_6 = QtGui.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(20, 140, 61, 16))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_7 = QtGui.QLabel(Dialog)
        self.label_7.setGeometry(QtCore.QRect(20, 170, 46, 13))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.le_name = QtGui.QLineEdit(Dialog)
        self.le_name.setGeometry(QtCore.QRect(80, 20, 351, 20))
        self.le_name.setObjectName(_fromUtf8("le_name"))
        self.le_url = QtGui.QLineEdit(Dialog)
        self.le_url.setGeometry(QtCore.QRect(80, 50, 351, 20))
        self.le_url.setObjectName(_fromUtf8("le_url"))
        self.le_request = QtGui.QLineEdit(Dialog)
        self.le_request.setGeometry(QtCore.QRect(80, 110, 351, 20))
        self.le_request.setObjectName(_fromUtf8("le_request"))
        self.le_typename = QtGui.QLineEdit(Dialog)
        self.le_typename.setGeometry(QtCore.QRect(80, 140, 351, 20))
        self.le_typename.setObjectName(_fromUtf8("le_typename"))
        self.le_srsname = QtGui.QLineEdit(Dialog)
        self.le_srsname.setGeometry(QtCore.QRect(80, 170, 121, 20))
        self.le_srsname.setObjectName(_fromUtf8("le_srsname"))
        self.combo_service = QtGui.QComboBox(Dialog)
        self.combo_service.setGeometry(QtCore.QRect(80, 80, 71, 22))
        self.combo_service.setObjectName(_fromUtf8("combo_service"))
        self.combo_version = QtGui.QComboBox(Dialog)
        self.combo_version.setGeometry(QtCore.QRect(230, 80, 69, 22))
        self.combo_version.setObjectName(_fromUtf8("combo_version"))
        self.pb_save = QtGui.QPushButton(Dialog)
        self.pb_save.setGeometry(QtCore.QRect(280, 170, 75, 23))
        self.pb_save.setObjectName(_fromUtf8("pb_save"))
        self.pb_cancel = QtGui.QPushButton(Dialog)
        self.pb_cancel.setGeometry(QtCore.QRect(360, 170, 75, 23))
        self.pb_cancel.setStatusTip(_fromUtf8(""))
        self.pb_cancel.setText(_fromUtf8("Cancel"))
        self.pb_cancel.setObjectName(_fromUtf8("pb_cancel"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.le_name, self.le_url)
        Dialog.setTabOrder(self.le_url, self.combo_service)
        Dialog.setTabOrder(self.combo_service, self.combo_version)
        Dialog.setTabOrder(self.combo_version, self.le_request)
        Dialog.setTabOrder(self.le_request, self.le_typename)
        Dialog.setTabOrder(self.le_typename, self.le_srsname)
        Dialog.setTabOrder(self.le_srsname, self.pb_cancel)
        Dialog.setTabOrder(self.pb_cancel, self.pb_save)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "name:", None))
        self.label_2.setText(_translate("Dialog", "url:", None))
        self.label_3.setText(_translate("Dialog", "service:", None))
        self.label_4.setText(_translate("Dialog", "version:", None))
        self.label_5.setText(_translate("Dialog", "request:", None))
        self.label_6.setText(_translate("Dialog", "typename:", None))
        self.label_7.setText(_translate("Dialog", "srsname:", None))
        self.pb_save.setText(_translate("Dialog", "Save", None))

