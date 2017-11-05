################WEBWORKER THREAD#############################################
#############################################################################
from PyQt4 import QtCore, QtGui
from ui.py.ui_pref import Ui_pref
#from settingsThread import settings_thread
from functions import *
import json


# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)

try:
     _fromUtf8= QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class Pref():

    def __init__(self, parenta):
        self.parent=parenta
        self.pref_dialog=QtGui.QDialog()
        self.pref_dialog.setWindowIcon(QtGui.QIcon(configs.icon_path))
        self.pref_ui = Ui_pref()
        self.pref_ui.setupUi(self.pref_dialog)
        self.dir=None
        self.loadStoragePath()
        self.pref_ui.saveBtn.setEnabled(False)

        QtCore.QObject.connect(self.pref_ui.browse, QtCore.SIGNAL(_fromUtf8("released()")), self.browsePath)
        QtCore.QObject.connect(self.pref_ui.saveBtn, QtCore.SIGNAL(_fromUtf8("released()")), self.saveSettings)
        QtCore.QObject.connect(self.pref_dialog, QtCore.SIGNAL(_fromUtf8("finished (int)")), self.closePref)

        self.pref_dialog.exec_()



    def alert(self,text):
        QtGui.QMessageBox.warning(self.pref_dialog,"Youtube Downloader", str(text))


    def closePref(self):
        self.parent.loadStoragePath()
        self.pref_dialog.close()

    def browsePath(self):
        self.pref_ui.saveBtn.setEnabled(True)
        defaultPath=self.pref_ui.path.text()
        self.dir=QtGui.QFileDialog.getExistingDirectory(self.pref_dialog, "Open Directory",defaultPath, QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontResolveSymlinks);
        self.pref_ui.path.setText(self.dir)

    def saveSettings(self):
        update("UPDATE settings SET value=? WHERE name='storage_path';",(self.dir,))
        self.pref_ui.saveBtn.setEnabled(False)
        self.loadStoragePath()
   



    def loadStoragePath(self):
        data=select("select value from settings where name='storage_path'").fetchone()
        self.pref_ui.path.setText(data[0])

