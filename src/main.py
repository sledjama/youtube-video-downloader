# To change this template, choose Tools | Templates
# and open the template in the editor.
version="0.1"
import sys
import os, re, subprocess, programs
from PyQt4 import QtCore, QtGui
import time
import json
import filecmp
from ui.py.ui_main import Ui_main
from classes.preference import pref
from functions import *
from classes.url import *
from classes.bg_process import backgroundProcess
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
        self.spawnit=None
        self.loadStoragePath()
        self.connectionErrorFlag=False
        
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowIcon(QtGui.QIcon(':/images/logo.png'))
        self.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)

        self.main_ui=Ui_main()
        self.main_ui.setupUi(self)
        self.setWindowTitle(QtGui.QApplication.translate("YoutubeDownloader", "Youtube Downloader - "+version, None))
        
        self.loadVideos()
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/logo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        QtCore.QObject.connect(self.main_ui.addURL, QtCore.SIGNAL(_fromUtf8("triggered()")), self.showInputForm)
        QtCore.QObject.connect(self.main_ui.actionPreferences, QtCore.SIGNAL(_fromUtf8("triggered()")), self.openSettings)
        QtCore.QObject.connect(self.main_ui.actionReportProblem, QtCore.SIGNAL(_fromUtf8("triggered()")), self.reportProblem)
        QtCore.QObject.connect(self.main_ui.videoTreeW, QtCore.SIGNAL(_fromUtf8("itemDoubleClicked(QTreeWidgetItem *,int)")), self.openFile)
        QtCore.QObject.connect(self.main_ui.searchLineEdit, QtCore.SIGNAL(_fromUtf8("textChanged (const QString&)")), self.searchDB)

        self.main_ui.videoTreeW.setColumnWidth(0, 350)
        self.main_ui.videoTreeW.setColumnWidth(1, 100)

        #lets add contextmenu to video lists


        self.actnPlay=QtGui.QAction("&Play video",self.main_ui.videoTreeW)
        QtCore.QObject.connect(self.actnPlay, QtCore.SIGNAL("triggered()"), self.playVideo )
        self.main_ui.videoTreeW.addAction(self.actnPlay)

        self.actnOpenLocation=QtGui.QAction("&Open video location",self.main_ui.videoTreeW)
        QtCore.QObject.connect(self.actnOpenLocation, QtCore.SIGNAL("triggered()"), self.openLocation )
        self.main_ui.videoTreeW.addAction(self.actnOpenLocation)

        self.actnRetry=QtGui.QAction("&Retry download",self.main_ui.videoTreeW)
        QtCore.QObject.connect(self.actnRetry, QtCore.SIGNAL("triggered()"), self.retryDownload )
        self.main_ui.videoTreeW.addAction(self.actnRetry)

        self.actnDelete=QtGui.QAction("&Remove",self.main_ui.videoTreeW)
        QtCore.QObject.connect(self.actnDelete, QtCore.SIGNAL("triggered()"), self.deleteVideo )
        self.main_ui.videoTreeW.addAction(self.actnDelete)

        self.actnDeleteVideo=QtGui.QAction("&Remove + Delete video",self.main_ui.videoTreeW)
        QtCore.QObject.connect(self.actnDeleteVideo, QtCore.SIGNAL("triggered()"), self.deleteVideoData )
        self.main_ui.videoTreeW.addAction(self.actnDeleteVideo)

        self.main_ui.videoTreeW.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu )

        #set column widths
        self.main_ui.videoTreeW.setColumnWidth(0,250)
        self.main_ui.videoTreeW.setColumnWidth(1,70)
        self.main_ui.videoTreeW.setColumnWidth(2,360)


    def alert(self,text):
        QtGui.QMessageBox.warning(self,"Youtube Downloader", str(text))

    def reportProblem(self):
        QtGui.QMessageBox.information(self, "Youtube Downloader", str("Send an email to ajayi@oluwaseun.com"))


    def openSettings(self):
        self.settings=pref(self)

    def deleteVideo(self):
        twi=self.main_ui.videoTreeW.selectedItems()[0]
        delete("DELETE FROM videos WHERE id=?", (twi.text(5),))
        self.loadVideos()

    def deleteVideoData(self):
        twi=self.main_ui.videoTreeW.selectedItems()[0]
        filepath=twi.text(6)+twi.text(0)+"_"+twi.text(4)+".mp4"
        if os.path.exists(filepath):
            os.remove(filepath)
        delete("DELETE FROM videos WHERE id=?", (twi.text(5),))
        self.loadVideos()

    def retryDownload(self):
        #youtube-dl takes time so we should skip the name check if it has been done
        twi=self.main_ui.videoTreeW.selectedItems()[0]
        if re.match("https?://",twi.text(0), re.IGNORECASE):
            self.thread_getname(twi.text(4))
        else:
            self.onDone(twi.text(0), twi.text(4))


    def playVideo(self):
        twi=self.main_ui.videoTreeW.selectedItems()[0]
        filepath=twi.text(6)+twi.text(0)+"_"+twi.text(4)+".mp4"
        print(filepath)

        if os.path.exists(filepath):
            os.startfile(filepath)
        else:
            self.alert("Video has been moved!")


    def openLocation(self):
        twi=self.main_ui.videoTreeW.selectedItems()[0]
        filepath=twi.text(6)+twi.text(0)+"_"+twi.text(4)+".mp4"
        print(filepath)
        subprocess.Popen(r'explorer /select, '+filepath)
        
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
        print(v_id)
        if re.match("^[-_a-zA-Z0-9]{11}$", v_id):
            fullURL="https://www.youtube.com/watch?v="+v_id
        elif re.match("^PL[-_a-zA-Z0-9]{32}$", v_id):

            fullURL="https://www.youtube.com/watch?list="+v_id
        else:
            self.alert("Not a valid youtube URL")
        #check if item already exist
        matches=self.main_ui.videoTreeW.findItems(v_id,QtCore.Qt.MatchFlag(),4)
        if matches.__len__()<1:
            #add to tree widget
            item=QtGui.QTreeWidgetItem(self.main_ui.videoTreeW)
            item.setText(0,fullURL)
            item.setText(1,"fetching URL...")
            item.setText(2,"...")
            item.setText(3,time.strftime("%d/%m/%Y %I:%M:%S"))
            item.setText(4,v_id)
            self.main_ui.videoTreeW.addTopLevelItem(item)
            self.thread_getname(v_id)
            
            #ret=os.system("youtube-dl.exe -g "+ytLink)
            #print(ret)
        else:
            #unselect any previously selected and select the possible duplicate
            for selectedItem in self.main_ui.videoTreeW.selectedItems():
                selectedItem.setSelected(False)
            matches[0].setSelected(True)


    def thread_getname(self, vID):
        if self.spawnit is not None and self.spawnit.isRunning():
            self.spawnit.quit()
        self.spawnit=backgroundProcess(youtubeProgram + " -e ", vID, "get_name")
        QtCore.QObject.connect(self.spawnit, QtCore.SIGNAL("nameReady(const QString&, const QString&)"), self.onDone)
        self.spawnit.start()

    def thread_getVideo(self, vID):
        self.dlit=backgroundProcess(youtubeProgram + " -c -o "+self.storage_path+"%(title)s_%(id)s.%(ext)s --newline --youtube-skip-dash-manifest --prefer-ffmpeg --recode-video mp4  -f 43 ", vID, "download_video")
        QtCore.QObject.connect(self.dlit, QtCore.SIGNAL("statusReady(const QString&, const QString&)"), self.onStatus)
        QtCore.QObject.connect(self.dlit, QtCore.SIGNAL("errorReady(const QString&, const QString&)"), self.onError)
        self.dlit.start()


    def onDone(self,ret,item2search):
        self.setStatusTip("")
        checkIfExists=select("SELECT id FROM videos WHERE video_id=?",(item2search,)).fetchone()
        if checkIfExists is None:
            insert("INSERT INTO videos (video_id, namex, sizex, storage_path, statusx) VALUES(?,?,?,?,?)",(item2search,ret, 0,self.storage_path,"Starting..."))
        else:
            update("UPDATE videos SET statusx=?",("Restarting...",))
        matches=self.main_ui.videoTreeW.findItems(item2search,QtCore.Qt.MatchFlag(),4)
        matches[0].setText(0,ret)
        matches[0].setText(1,"...")
        #lets append video ids so users can locate video on youtube later on
        self.thread_getVideo(item2search)


    def onError(self,ret,item2search):

        self.setStatusTip(ret)


    def onStatus(self,ret,item2search):
        self.setStatusTip("")
        matches=self.main_ui.videoTreeW.findItems(item2search,QtCore.Qt.MatchFlag(),4)
        size=re.findall(r'(\d+\.\d+MiB|\d+\.\d+KiB)', ret)

        extractedSize=None
        if size.__len__()>0:
            extractedSize=size[0]
            print(size)
            matches[0].setText(1,extractedSize)

        #display human readable status
        if ret.startswith("Deleting original file"):
            ret="Download complete"

        ret=re.sub("\[youtube\]\s[-_a-zA-Z0-9]{11}:\s","", ret)
        ret=re.sub("\[download\]\sDestination:\s","Destination:", ret)
        ret=re.sub("\[download\]\s+","", ret)
        ret=re.sub("\[ffmpeg\]\s","", ret)

        matches[0].setText(2,ret)

        if extractedSize is not None:
            params=(self.storage_path,ret,extractedSize,item2search,)
            update("update videos set storage_path=?, statusx=?, sizex=? where video_id=?",params)
        else:
            #skip size
            params=(self.storage_path,ret,item2search,)
            update("update videos set storage_path=?, statusx=? where video_id=?",params)


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
        print(self.storage_path)

    def loadVideos(self):
        data=select("SELECT id, video_id, namex, sizex, datesx, storage_path, statusx FROM videos ORDER BY id DESC limit 100").fetchall()
        self.populateTreeWidget(data)
        self.main_ui.videoTreeW.setColumnHidden(4,True)
        self.main_ui.videoTreeW.setColumnHidden(5,True)
        self.main_ui.videoTreeW.setColumnHidden(6,True)
        self.main_ui.videoTreeW.setColumnHidden(7,True)
        del data


    def openFile(self, twi, indx):
        self.alert(twi.text(6)+twi.text(0)+"_"+twi.text(4)+".mp4")
        os.startfile(twi.text(6)+twi.text(0)+"_"+twi.text(4)+".mp4")

    def searchDB(self, searchText):
        #though i dont see most saving more than 10,000 videos
        #this gets called everytime a text changes in the search box
        #TODO, will rerun a test to see if this is more efficent or to put namex/id in list on first searchdb call
        #then search the list then come after the row in DB using the id

        data=select("SELECT id, video_id, namex, sizex, datesx, storage_path, statusx FROM videos WHERE namex like ? ORDER BY id DESC", ("%"+searchText+"%",)).fetchall()
        self.populateTreeWidget(data)

    def populateTreeWidget(self, data):
        self.main_ui.videoTreeW.clear()
        for x in data:
            item=QtGui.QTreeWidgetItem(self.main_ui.videoTreeW)
            item.setText(0, str(x[2]))
            item.setText(1, str(x[3]))
            item.setText(2,  str(x[6]))
            item.setText(3,  str(x[4]))
            item.setText(4,  str(x[1]))
            item.setText(5,  str(x[0]))
            item.setText(6,  str(x[5]))
            self.main_ui.videoTreeW.insertTopLevelItem(0,item)



if __name__ == "__main__":
        
    #try:
    app = QtGui.QApplication(sys.argv)
    myapp = YoutubeDownloader()
    myapp.show()
    sys.exit(app.exec_())
    #except:
        #pass



