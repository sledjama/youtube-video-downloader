"""
This is the GUI for the preference or settings where users setup the default download folder to use.
Whatever settings here goes to sqlite for persistence.
"""
from PyQt4 import QtCore, QtGui
from ui.py.ui_pref import Ui_pref
from functions import *
import json

try:
     _fromUtf8= QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    
class Pref():
    def __init__(self, parent):
        """
        Draw the QDialog, make parent available as self.parent and load saved storage path
        :param parent: Refers to the main GUI instance
        """
        self.parent = parent
        self.pref_dialog = QtGui.QDialog()
        self.pref_dialog.setWindowIcon(QtGui.QIcon(configs.icon_path))
        self.pref_ui = Ui_pref()
        self.pref_ui.setupUi(self.pref_dialog)
        self.dir = None
        self.loadStoragePath()
        self.pref_ui.saveBtn.setEnabled(False)

        QtCore.QObject.connect(self.pref_ui.browse, QtCore.SIGNAL(_fromUtf8("released()")),
                               self.browsePath)
        QtCore.QObject.connect(self.pref_ui.saveBtn, QtCore.SIGNAL(_fromUtf8("released()")),
                               self.saveSettings)
        QtCore.QObject.connect(self.pref_dialog, QtCore.SIGNAL(_fromUtf8("finished (int)")),
                               self.closePref)
        self.pref_dialog.exec_()

    def alert(self, text):
        """
        Warning shots
        :param text: the warning to display
        :return:
        """
        QtGui.QMessageBox.warning(self.pref_dialog, "Youtube Downloader", str(text))

    def closePref(self):
        """
        When closing the UI, we need to tell parent to checkout changes.
        :return:
        """
        self.parent.load_storage_path()
        self.pref_dialog.close()

    def browsePath(self):
        """
        Let users select directory to save videos
        :return:
        """
        self.pref_ui.saveBtn.setEnabled(True)
        defaultPath = self.pref_ui.path.text()
        self.dir = QtGui.QFileDialog.getExistingDirectory(self.pref_dialog, "Open Directory",
                                                          defaultPath,
                                                          QtGui.QFileDialog.ShowDirsOnly |
                                                          QtGui.QFileDialog.DontResolveSymlinks)
        self.pref_ui.path.setText(self.dir)

    def saveSettings(self):
        """
        This is called by the save signal
        :return:
        """
        update("UPDATE settings SET value=? WHERE name='storage_path';", (self.dir,))
        self.pref_ui.saveBtn.setEnabled(False)
        self.loadStoragePath()

    def loadStoragePath(self):
        """
        Load storage path from DB to UI
        :return:
        """
        data = select("select value from settings where name='storage_path'").fetchone()
        self.pref_ui.path.setText(data[0])
