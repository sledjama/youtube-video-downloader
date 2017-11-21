"""



"""
import sys
import os
import re
import subprocess
import programs

# convert ui to .py first
# from ui import compile

from PyQt4 import QtCore, QtGui
import time
from ui.py.ui_main import Ui_main
from classes.preference import Pref
from functions import *
from classes.bg_process import backgroundProcess
from _version import __version__

createDB()

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class YoutubeDownloader(QtGui.QMainWindow):

    def __init__(self, parent=None):
        """this is called first
        """

        self.storage_path = ""
        self.spawnit = None
        self.load_storage_path()
        
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowIcon(QtGui.QIcon(configs.icon_path))
        self.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)

        self.main_ui=Ui_main()
        self.main_ui.setupUi(self)
        self.setWindowTitle(QtGui.QApplication.translate("YoutubeDownloader", "Youtube Downloader - "+__version__, None))
        
        self.load_videos()

        QtCore.QObject.connect(self.main_ui.addURL, QtCore.SIGNAL(_fromUtf8("triggered()")), self.show_input_form)
        QtCore.QObject.connect(self.main_ui.actionPreferences, QtCore.SIGNAL(_fromUtf8("triggered()")), self.open_settings)
        QtCore.QObject.connect(self.main_ui.actionReportProblem, QtCore.SIGNAL(_fromUtf8("triggered()")), self.report_problem)
        QtCore.QObject.connect(self.main_ui.videoTreeW, QtCore.SIGNAL(_fromUtf8("itemDoubleClicked(QTreeWidgetItem *,int)")), self.open_file)
        QtCore.QObject.connect(self.main_ui.searchLineEdit, QtCore.SIGNAL(_fromUtf8("textChanged (const QString&)")), self.search_database)

        # lets add contextmenu to video lists
        self.actnPlay=QtGui.QAction("&Play video",self.main_ui.videoTreeW)
        QtCore.QObject.connect(self.actnPlay, QtCore.SIGNAL("triggered()"), self.play_video )
        self.main_ui.videoTreeW.addAction(self.actnPlay)

        self.actnOpenLocation=QtGui.QAction("&Open video location",self.main_ui.videoTreeW)
        QtCore.QObject.connect(self.actnOpenLocation, QtCore.SIGNAL("triggered()"), self.open_location )
        self.main_ui.videoTreeW.addAction(self.actnOpenLocation)

        self.actnRetry=QtGui.QAction("&Retry download",self.main_ui.videoTreeW)
        QtCore.QObject.connect(self.actnRetry, QtCore.SIGNAL("triggered()"), self.retry_download )
        self.main_ui.videoTreeW.addAction(self.actnRetry)

        self.actnDelete=QtGui.QAction("&Remove",self.main_ui.videoTreeW)
        QtCore.QObject.connect(self.actnDelete, QtCore.SIGNAL("triggered()"), self.delete_video )
        self.main_ui.videoTreeW.addAction(self.actnDelete)

        self.actnDeleteVideo=QtGui.QAction("&Remove + Delete video",self.main_ui.videoTreeW)
        QtCore.QObject.connect(self.actnDeleteVideo, QtCore.SIGNAL("triggered()"), self.delete_video_data )
        self.main_ui.videoTreeW.addAction(self.actnDeleteVideo)

        self.main_ui.videoTreeW.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu )

        # set column widths
        self.main_ui.videoTreeW.setColumnWidth(0,250)
        self.main_ui.videoTreeW.setColumnWidth(1,70)
        self.main_ui.videoTreeW.setColumnWidth(2,310)

    def alert(self,text):
        QtGui.QMessageBox.warning(self,"Youtube Downloader", str(text))

    def report_problem(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/sledjama/youtube-video-downloader/issues"))

    def open_settings(self):
        Pref(self)

    def delete_video(self):
        twi=self.main_ui.videoTreeW.selectedItems()[0]
        delete("DELETE FROM videos WHERE id=?", (twi.text(5),))
        self.load_videos()

    def delete_video_data(self):
        twi=self.main_ui.videoTreeW.selectedItems()[0]
        filepath=twi.text(6)+twi.text(0)+"_"+twi.text(4)+".mp4"
        if os.path.exists(filepath):
            os.remove(filepath)
        delete("DELETE FROM videos WHERE id=?", (twi.text(5),))
        self.load_videos()

    def retry_download(self):
        # youtube-dl takes time so we should skip the name check if it has been done
        twi=self.main_ui.videoTreeW.selectedItems()[0]
        if re.match("https?://",twi.text(0), re.IGNORECASE):
            self.thread_getname(twi.text(4))
        else:
            self.on_thread_name(twi.text(0), twi.text(4))

    def play_video(self):
        twi=self.main_ui.videoTreeW.selectedItems()[0]
        filepath=twi.text(6)+twi.text(0)+"_"+twi.text(4)+".mp4"
        print(filepath)

        if os.path.exists(filepath):
            os.startfile(filepath)
        else:
            self.alert("Video has been moved!")

    def open_location(self):
        twi=self.main_ui.videoTreeW.selectedItems()[0]
        filepath=twi.text(6)+twi.text(0)+"_"+twi.text(4)+".mp4"
        subprocess.Popen(r'explorer /select, '+filepath)
        
    def show_input_form(self):
        cliptext=QtGui.QApplication.clipboard().text()
        matchingNumbers=re.search(r'(http|https)://(www.)?youtube',cliptext) # it could be .ng or .com so lets leave the last section out
        if matchingNumbers is None:
            cliptext = ""
        returnedURL, returnedStatus = QtGui.QInputDialog.getText(self, "Paste Youtube link",
                                                                 "Paste Youtube link below to add it to your queue:\t\t\t\t\t\t\t\t",
                                                                 QtGui.QLineEdit.Normal, cliptext);
        # once url is gotten, lets add it to the tree widget as tree widget it
        if returnedStatus and returnedURL.strip() != "":
            self.add_to_queue(returnedURL)
        
    def add_to_queue(self, youtube_link):
        v_id = video_id(youtube_link)
        if re.match("^[-_a-zA-Z0-9]{11}$", v_id):
            fullURL = "https://www.youtube.com/watch?v="+v_id
        elif re.match("^PL[-_a-zA-Z0-9]{32}$", v_id):

            fullURL = "https://www.youtube.com/watch?list="+v_id
        else:
            self.alert("Not a valid youtube URL")

        # check if item already exist
        matches = self.main_ui.videoTreeW.findItems(v_id,QtCore.Qt.MatchFlag(),4)
        if matches.__len__()<1:
            # add to tree widget, we mock it like it is coming from DB
            data=(['' , v_id, fullURL, 'fetching URL...', time.strftime("%d/%m/%Y %I:%M:%S"), self.storage_path, '...'],)
            self.populate_tree_widget(data)
            self.thread_getname(v_id)
        else:
            # unselect any previously selected and select the possible duplicate
            for selectedItem in self.main_ui.videoTreeW.selectedItems():
                selectedItem.setSelected(False)
            matches[0].setSelected(True)

    def thread_getname(self, vID):
        # print("thread_getname", vID)
        if self.spawnit is not None and self.spawnit.isRunning():
            self.spawnit.quit()
        self.spawnit = backgroundProcess(configs.youtubeProgram + " -e ", vID, "get_name")
        QtCore.QObject.connect(self.spawnit, QtCore.SIGNAL("nameReady(const QString&, const QString&)"), self.on_thread_name)
        self.spawnit.start()

    def is_file_downloaded(self, fileToCheck):
        data = select("select namex from videos where video_id=?", (fileToCheck,)).fetchone()
        if data is not None:
            file_path = os.path.join(self.storage_path, str(data[0])+"_"+fileToCheck+".mp4")
        return os.path.isfile(file_path)

    def get_video_thread(self, vID):
        # don't download if file still exists to prevent accidental re-download
        self.dlit = backgroundProcess(configs.youtubeProgram + " -c -o "+self.storage_path+"%(title)s_%(id)s.%(ext)s --newline --youtube-skip-dash-manifest --prefer-ffmpeg --recode-video mp4  -f 43 ", vID, "download_video")
        QtCore.QObject.connect(self.dlit, QtCore.SIGNAL("statusReady(const QString&, const QString&)"), self.on_status)
        QtCore.QObject.connect(self.dlit, QtCore.SIGNAL("errorReady(const QString&, const QString&)"), self.on_error)
        self.dlit.start()

    def on_thread_name(self, ret, item2search):
        self.setStatusTip("")
        checkIfExists = select("SELECT id FROM videos WHERE video_id=?",(item2search,)).fetchone()

        matches=self.main_ui.videoTreeW.findItems(item2search,QtCore.Qt.MatchFlag(),4)
        matches[0].setText(0,ret)

        if checkIfExists is None:
            # if video exists in treewidget
            insert("INSERT INTO videos (video_id, namex, sizex, storage_path, statusx) VALUES(?,?,?,?,?)", (item2search, ret, 0, self.storage_path, "Starting..."))
            self.get_video_thread(item2search)
        elif not self.is_file_downloaded(item2search):
            # if video has not been downloaded and marked complete in DB
            update("UPDATE videos SET statusx=?", ("Restarting...",))
            self.get_video_thread(item2search)
        else:
            self.alert("File already downloaded")

    def on_error(self, ret, item2search):
        self.setStatusTip(ret)

    def on_status(self, ret, item2search):
        self.setStatusTip("")
        matches = self.main_ui.videoTreeW.findItems(item2search,QtCore.Qt.MatchFlag(), 4)
        size = re.findall(r'(\d+\.\d+%|\d+\.\d+GiB|\d+\.\d+MiB|\d+\.\d+KiB)', ret)

        extractedSize = None
        if len(size) > 0:
            extractedSize = size[0]
            # only set the size first index is NOT d%
            if size[0][-1:]=="%":
                matches[0].setText(1,size[1])
                extractedSize=size[1]
            progressBarBG = self.main_ui.videoTreeW.itemWidget(matches[0], 2)
            progressBar = progressBarBG.findChild(type(QtGui.QProgressBar()))
            progressBar.setMinimum(0)
            convertedSizeKB = []
            percentDone = 0
            for x in size:
                if x[-3:] == "GiB":
                    convertedSizeKB.append(int(float(x[:-3]))*1024*1024)
                elif x[-3:] == "MiB":
                    convertedSizeKB.append(int(float(x[:-3]))*1024)
                elif x[-3:] == "KiB":
                    convertedSizeKB.append(int(float(x[:-3])))
                elif x[-1:] == "%":
                    percentDone = int(float(x[:-3]))
            progressBar.setMaximum(100)
            if percentDone > 0:
                progressBar.setValue(percentDone)
        ret = re.sub("\[youtube\]\s[-_a-zA-Z0-9]{11}:\s", "", ret)
        ret = re.sub("\[download\]\sDestination:\s", "Destination:", ret)
        ret = re.sub("\[download\]\s+", "", ret)
        ret = re.sub("\[ffmpeg\]\s", "", ret)

        if ret.startswith("Deleting original file") or ret.startswith("Not converting video file "):
            ret = "Download complete"

        if extractedSize is not None:
            params = (self.storage_path, ret, extractedSize, item2search,)
            update("update videos set storage_path=?, statusx=?, sizex=? where video_id=?", params)
        else:
            # skip size
            params=(self.storage_path, ret, item2search,)
            update("update videos set storage_path=?, statusx=? where video_id=?",params)

    def load_storage_path(self):
        data = select("select value from settings where name='storage_path'").fetchone()
        if data[0]!="":
            self.storage_path=data[0]+"\\"
        else:
            self.storage_path=""

    def load_videos(self):
        data = select("SELECT id, video_id, namex, sizex, datesx, storage_path, statusx FROM videos ORDER BY id DESC limit 100").fetchall()
        self.main_ui.videoTreeW.clear()
        self.populate_tree_widget(data)
        self.main_ui.videoTreeW.setColumnHidden(4, True)
        self.main_ui.videoTreeW.setColumnHidden(5, True)
        self.main_ui.videoTreeW.setColumnHidden(6, True)
        self.main_ui.videoTreeW.setColumnHidden(7, True)

    def open_file(self, twi, indx):
        os.startfile(twi.text(6)+twi.text(0)+"_"+twi.text(4)+".mp4")

    def search_database(self, searchText):
        # though i dont see most saving more than 10,000 videos
        # this gets called everytime a text changes in the search box
        data = select("SELECT id, video_id, namex, sizex, datesx, storage_path, statusx FROM videos "
                      "WHERE namex like ? ORDER BY id DESC", ("%"+searchText+"%",)).fetchall()
        self.main_ui.videoTreeW.clear()
        self.populate_tree_widget(data)

    def populate_tree_widget(self, data):
        for x in data:
            item=QtGui.QTreeWidgetItem(self.main_ui.videoTreeW)
            item.setText(0, str(x[2]))
            item.setText(1, str(x[3]))
            item.setText(3,  str(x[4]))
            item.setText(4,  str(x[1]))
            item.setText(5,  str(x[0]))
            item.setText(6,  str(x[5]))
            # create placeholder widget so we can resize widget and not progressbar itself
            progressBarBG=QtGui.QWidget(self.main_ui.videoTreeW)
            # create progressbar and assign parent
            downloadProgressBar=QtGui.QProgressBar(progressBarBG)
            downloadProgressBar.setGeometry(QtCore.QRect(4,2, 300, 14))
            downloadProgressBar.setAlignment(QtCore.Qt.AlignHCenter)

            # if download is complete, show green bars
            if str(x[6]) == "Download complete":
                downloadProgressBar.setMaximum(100)
                downloadProgressBar.setMinimum(0)
                downloadProgressBar.setValue(100)

            self.main_ui.videoTreeW.setItemWidget(item, 2, progressBarBG)
            self.main_ui.videoTreeW.insertTopLevelItem(0, item)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    youtube_app = YoutubeDownloader()
    youtube_app.show()
    sys.exit(app.exec_())