# To change this template, choose Tools | Templates
# and open the template in the editor.
version="0.1"
import sys
import os, re, subprocess
from PyQt4 import QtCore, QtGui
import time
import json
import filecmp
from ui_main import Ui_main
from preference import pref
from functions import *
from url import *
from bg_process import backgroundProcess
import sqlite3


createDB()

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)

try:
     _fromUtf8= QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s
    


class YoutubeDownloader(QtGui.QMainWindow):
    def __init__(self, parent=None):
        """this is called first
        """

        self.storage_path=""
        self.loadStoragePath()
        
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowIcon(QtGui.QIcon(':/images/logo.png'))
        self.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)

        self.main_ui=Ui_main()
        self.main_ui.setupUi(self)
        self.setWindowTitle(QtGui.QApplication.translate("YoutubeDownloader", "Youtube Downloader - "+version, None))
        
        
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/logo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        QtCore.QObject.connect(self.main_ui.addURL, QtCore.SIGNAL(_fromUtf8("triggered()")), self.showInputForm)
        QtCore.QObject.connect(self.main_ui.actionPreferences, QtCore.SIGNAL(_fromUtf8("triggered()")), self.openSettings)
        self.main_ui.videoTreeW.setColumnWidth(0, 350)
        self.main_ui.videoTreeW.setColumnWidth(1, 100)


    def alert(self,text):
        QtGui.QMessageBox.warning(self,"Youtube Downloader", str(text))


    def openSettings(self):
        self.settings=pref(self)

        
    def showInputForm(self):
        cliptext=QtGui.QApplication.clipboard().text()
        matchingNumbers=re.search(r'(http|https)://(www.)?youtube',cliptext) #it could be .ng or .com so lets leave the last section out
        if matchingNumbers is None:
            cliptext=""
        returnedURL,returnedStatus=QtGui.QInputDialog.getText(self, "Paste Youtube link","Paste Youtube link below to add it to your queue:\t\t\t\t\t\t\t\t", QtGui.QLineEdit.Normal, cliptext);
        #once url is gotten, lets add it to the tree widget as tree widget it
        if returnedStatus and returnedURL.strip()!="":
            self.addToQueue(returnedURL)
        
    def addToQueue(self,ytLink):
        v_id=video_id(ytLink)
        #check if item already exist
        matches=self.main_ui.videoTreeW.findItems(v_id,QtCore.Qt.MatchFlag(),4)
        if matches.__len__()<1:
            #add to tree widget
            item=QtGui.QTreeWidgetItem(self.main_ui.videoTreeW)
            item.setText(0,ytLink)
            item.setText(1,"fetching URL...")
            item.setText(2,"...")
            item.setText(3,time.strftime("%d/%m/%Y %I:%M:%S"))
            item.setText(4,v_id)
            self.main_ui.videoTreeW.addTopLevelItem(item)
            self.spawnit=backgroundProcess("youtube-dl.exe" + " -e ", v_id, "get_name")
            QtCore.QObject.connect(self.spawnit, QtCore.SIGNAL("nameReady(const QString&, const QString&)"), self.onDone)
            self.spawnit.start()
            
            #ret=os.system("youtube-dl.exe -g "+ytLink)
            #print(ret)
        else:
            #unselect any previously selected and select the possible duplicate
            for selectedItem in self.main_ui.videoTreeW.selectedItems():
                selectedItem.setSelected(False)
            matches[0].setSelected(True)

    def onDone(self,ret,item2search):
        print(self.storage_path)
        matches=self.main_ui.videoTreeW.findItems(item2search,QtCore.Qt.MatchFlag(),4)
        matches[0].setText(0,ret)
        matches[0].setText(1,"Downloading video")
        self.dlit=backgroundProcess("youtube-dl.exe" + " -o "+self.storage_path+"%(title)s_%(id)s.%(ext)s --newline ", item2search, "download_video")
        QtCore.QObject.connect(self.dlit, QtCore.SIGNAL("statusReady(const QString&, const QString&)"), self.onStatus)
        self.dlit.start()

    def onStatus(self,ret,item2search):
        matches=self.main_ui.videoTreeW.findItems(item2search,QtCore.Qt.MatchFlag(),4)
        matches[0].setText(2,ret)
        self.alert(ret)
        
    def launchFile(self, theFile):
        os.startfile(theFile,"open")

    def showAlert(self, msg):
        QtGui.QMessageBox.information(self,"Youtube Downloader",msg, QtGui.QMessageBox.Ok)



    def loadStoragePath(self):
        data=select("select value from settings where name='storage_path'").fetchone()
        if data[0]!="":
            self.storage_path=data[0]+"\\"
        else:
            self.storage_path=""





if __name__ == "__main__":
        
    #try:
    app = QtGui.QApplication(sys.argv)
    myapp = YoutubeDownloader()
    myapp.show()
    sys.exit(app.exec_())
    #except:
        #pass



