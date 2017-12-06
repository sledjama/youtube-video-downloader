"""

This is the Application's entry point and should be run directly.
It simply builds a GUI, creates an SQLite database if it does not exist,
if it exists, it loads recently downloaded movies from the SQLite database
into the QTreeWidget.
To get the videos, this application calls the commandline youtube-dl in such
a way that it is able to receive the outputs from the command line.
Since seeing is believing, the output is interpreted to work with the
QProgressBar.

Future:
The commandline youtube-dl works with other sites, e.g lynda.com etc.
so the future is to have a software that is able to download from these sites.


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
from classes.bg_process import BackgroundProcess
from _version import __version__

createDB()

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class YoutubeDownloader(QtGui.QMainWindow):

    def __init__(self, parent=None):
        """
        Application's entry, initializes everything we need to build GUI
        and populate QTreeWidget with initial data

            Args:
                parent: Currently this has no parent
            Returns:
                None

            """

        self.storage_path = ""
        self.spawnit = None
        self.load_storage_path()
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowIcon(QtGui.QIcon(configs.icon_path))
        self.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.main_ui = Ui_main()
        self.main_ui.setupUi(self)
        self.setWindowTitle(QtGui.QApplication.translate("YoutubeDownloader",
                                                         "Youtube Downloader - "+__version__,
                                                         None))
        self.load_videos()

        # do the signal-slots
        QtCore.QObject.connect(self.main_ui.addURL, QtCore.SIGNAL(_fromUtf8("triggered()")),
                               self.show_input_form)
        QtCore.QObject.connect(self.main_ui.actionPreferences, QtCore.SIGNAL(_fromUtf8("triggered()")),
                               self.open_settings)
        QtCore.QObject.connect(self.main_ui.actionReportProblem, QtCore.SIGNAL(_fromUtf8("triggered()")),
                               self.report_problem)
        QtCore.QObject.connect(self.main_ui.videoTreeW, QtCore.SIGNAL(
                               _fromUtf8("itemDoubleClicked(QTreeWidgetItem *,int)")),
                               self.open_file)
        QtCore.QObject.connect(self.main_ui.searchLineEdit, QtCore.SIGNAL(
                               _fromUtf8("textChanged (const QString&)")), self.search_database)

        # lets add contextmenu to video lists
        self.actnPlay = QtGui.QAction("&Play video", self.main_ui.videoTreeW)
        QtCore.QObject.connect(self.actnPlay, QtCore.SIGNAL("triggered()"), self.play_video)
        self.main_ui.videoTreeW.addAction(self.actnPlay)

        self.actnOpenLocation = QtGui.QAction("&Open video location", self.main_ui.videoTreeW)
        QtCore.QObject.connect(self.actnOpenLocation, QtCore.SIGNAL("triggered()"), self.open_location_win)
        self.main_ui.videoTreeW.addAction(self.actnOpenLocation)

        self.actnRetry = QtGui.QAction("&Retry download", self.main_ui.videoTreeW)
        QtCore.QObject.connect(self.actnRetry, QtCore.SIGNAL("triggered()"), self.retry_download)
        self.main_ui.videoTreeW.addAction(self.actnRetry)

        self.actnDelete = QtGui.QAction("&Remove", self.main_ui.videoTreeW)
        QtCore.QObject.connect(self.actnDelete, QtCore.SIGNAL("triggered()"), self.delete_video )
        self.main_ui.videoTreeW.addAction(self.actnDelete)

        self.actnDeleteVideo = QtGui.QAction("&Remove + Delete video", self.main_ui.videoTreeW)
        QtCore.QObject.connect(self.actnDeleteVideo, QtCore.SIGNAL("triggered()"), self.delete_video_data )
        self.main_ui.videoTreeW.addAction(self.actnDeleteVideo)

        self.main_ui.videoTreeW.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        # set column widths
        self.main_ui.videoTreeW.setColumnWidth(0, 250)
        self.main_ui.videoTreeW.setColumnWidth(1, 70)
        self.main_ui.videoTreeW.setColumnWidth(2, 310)

    def alert(self, warning_text):
        """
        Application-wide convenience method for warning users

                   Args:
                       warning_text: The text to display to the user
                   Returns:
                       None
        """
        QtGui.QMessageBox.warning(self, "Youtube Downloader", str(warning_text))

    def report_problem(self):
        """
        This method gets called when there is an issue with the application
        that needs to be reported, It simply opens the application's issues
        page on github.

               Args:
                   None: No argument required
               Returns:
                   None

        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/sledjama/youtube-video-downloader/issues"))

    def open_settings(self):
        """
        This calls the Pref class that allows users setup their preferred settings
        We pass self into Pref, just so we can access the objects of this class from Pref


               Args:
                   None: No argument is required
               Returns:
                   None

        """
        Pref(self)

    def delete_video(self):
        """
        This is a SLOT from the QTreeWidgetItem's right click, when users select to delete a video entry
            this gets called. This currently deletes a video at a time, it can be stressful to delete many
            videos but it also reduces accidental deletions.

               Args:
                   None: No argument required except default self
               Returns:
                   None

        """
        twi = self.main_ui.videoTreeW.selectedItems()[0]
        delete("DELETE FROM videos WHERE id=?", (twi.text(5),))
        self.load_videos()

    def delete_video_data(self):
        """
        This is a contextmenu selection call to delete both video entry and video file on hard drive
            read more about this removal method here: https://stackoverflow.com/questions/10840533/most-pythonic-way-to-delete-a-file-which-may-not-exist

               Args:
                   None: No argument required exceopt the default self
               Returns:
                   None

        """
        twi = self.main_ui.videoTreeW.selectedItems()[0]
        file_path = twi.text(6)+twi.text(0)+"_"+twi.text(4)+".mp4"

        try:
            os.remove(file_path)
        except OSError:
            pass

        delete("DELETE FROM videos WHERE id=?", (twi.text(5),))
        self.load_videos()

    def retry_download(self):
        """
        This is an attempt to redownload a video, We will be skipping the name check if we already have the name

               Args:
                   None: No argument required exceopt the default self
               Returns:
                   None

        """
        twi = self.main_ui.videoTreeW.selectedItems()[0]
        if re.match("https?://", twi.text(0), re.IGNORECASE):
            self.thread_getname(twi.text(4))
        else:
            self.on_thread_name(twi.text(0), twi.text(4))

    def play_video(self):
        """
        This tries to play the selected video, this is called from the contextmenu selected by the user
            read more about this file access approach here:
            https://stackoverflow.com/questions/10840533/most-pythonic-way-to-delete-a-file-which-may-not-exist

               Args:
                   None: No argument required exceopt the default self
               Returns:
                   None

        """
        twi = self.main_ui.videoTreeW.selectedItems()[0]
        filepath = twi.text(6)+twi.text(0)+"_"+twi.text(4)+".mp4"

        try:
            os.startfile(filepath)
        except OSError:
            self.alert("Video has been moved!")

    def open_location_win(self):
        """
        This is a contextmenu selection call to open the file location on windows

               Args:
                   None: No argument required exceopt the default self
               Returns:
                   None

        """
        twi = self.main_ui.videoTreeW.selectedItems()[0]
        file_path = twi.text(6) + twi.text(0) + "_" + twi.text(4) + ".mp4"
        subprocess.Popen(r'explorer /select, '+file_path+"d")
        
    def show_input_form(self):
        """
        This opens a QInputDialog to allow users paste the youtube link
           this takes the initiative to grab the clipboard content, if it contains a youtube link
           it does the paste for the user

               Args:
                   None: No argument required exceopt the default self
               Returns:
                   None

        """

        cliptext = QtGui.QApplication.clipboard().text()
        # it could be .ng or .com so lets leave the last section out
        matchingNumbers = re.search(r'(http|https)://(www.)?youtube', cliptext)
        if matchingNumbers is None:
            cliptext = ""
        returnedURL, returnedStatus = QtGui.QInputDialog.getText(self, "Paste Youtube link",
                                                                 "Paste Youtube link below to add it "
                                                                 "to your queue:\t\t\t\t\t\t\t\t",
                                                                 QtGui.QLineEdit.Normal, cliptext)
        # once url is gotten, lets add it to the tree widget as tree widget it
        if returnedStatus and returnedURL.strip() != "":
            self.add_to_queue(returnedURL)
        
    def add_to_queue(self, youtube_link):
        """
        Adds a youtube link to the QTreeWidget, before adding, it should check if the video
            already exists in the QTreeWidget

               Args:
                   youtube_link: Accepts the youtube link in any of the possible youtube formats
               Returns:
                   None

        """
        v_id = video_id(youtube_link)
        if re.match("^[-_a-zA-Z0-9]{11}$", v_id):
            fullURL = "https://www.youtube.com/watch?v="+v_id
        elif re.match("^PL[-_a-zA-Z0-9]{32}$", v_id):

            fullURL = "https://www.youtube.com/watch?list="+v_id
        else:
            self.alert("Not a valid youtube URL")

        # check if item already exist
        matches = self.main_ui.videoTreeW.findItems(v_id,QtCore.Qt.MatchFlag(),4)
        if not matches:
            # add to tree widget, we mock it like it is coming from DB
            data = (['', v_id, fullURL, 'fetching URL...', time.strftime("%d/%m/%Y %I:%M:%S"),
                     self.storage_path, '...'],)
            self.populate_tree_widget(data)
            self.thread_getname(v_id)
        else:
            # unselect any previously selected and select the possible duplicate
            for selectedItem in self.main_ui.videoTreeW.selectedItems():
                selectedItem.setSelected(False)
            matches[0].setSelected(True)

    def thread_getname(self, vID):
        """
        Thread_getname gets the title of the youtube link by the 11 character youtube ID
         or playlist ID.
         This will change bacause there will be support for other sites in furture updates

               Args:
                   vID:  11 character youtube video ID or playlist IDs.
               Returns:
                   None

        """

        if self.spawnit is not None and self.spawnit.isRunning():
            self.spawnit.quit()
        self.spawnit = BackgroundProcess(configs.youtubeProgram + " -e ", vID, "get_name")
        QtCore.QObject.connect(self.spawnit, QtCore.SIGNAL("nameReady(const QString&, const QString&)"),
                               self.on_thread_name)
        self.spawnit.start()

    def is_file_downloaded(self, fileToCheck):
        """
        Verifies if the video exists in database and on  file

               Args:
                   fileToCheck: this is the video ID to check for
               Returns:
                   Boolean: if file exists

        """
        data = select("select namex from videos where video_id=?", (fileToCheck,)).fetchone()
        if data is not None:
            file_path = os.path.join(self.storage_path, str(data[0])+"_"+fileToCheck+".mp4")
            return os.path.isfile(file_path)
        else:
            return False

    def get_video_thread(self, video_id):
        """
        This creates a thread which downloads the video,  don't download if file still exists
        to prevent accidental re-download

               Args:
                   video_id: youtube video ID
               Returns:
                   None

        """

        self.dlit = BackgroundProcess(configs.youtubeProgram + " -c -o "+self.storage_path+"%(title)s_%(id)s.%(ext)s --newline --youtube-skip-dash-manifest --prefer-ffmpeg --recode-video mp4  -f 43 ", video_id, "download_video")
        QtCore.QObject.connect(self.dlit, QtCore.SIGNAL("statusReady(const QString&, const QString&)"), self.on_status)
        QtCore.QObject.connect(self.dlit, QtCore.SIGNAL("errorReady(const QString&, const QString&)"), self.on_error)
        self.dlit.start()

    def on_thread_name(self, returned_name, item2search):
        """
        This is called from the video download thread, if the commandline returns a video name

               Args:
                   returned_name: This is the returned name from youtube
                   item2search: This is the video ID being searched.
               Returns:
                   None

        """

        self.setStatusTip("")
        checkIfExists = select("SELECT id FROM videos WHERE video_id=?", (item2search,)).fetchone()

        matches = self.main_ui.videoTreeW.findItems(item2search, QtCore.Qt.MatchFlag(), 4)
        matches[0].setText(0, returned_name)

        if checkIfExists is None:
            # if video exists in treewidget
            insert("INSERT INTO videos (video_id, namex, sizex, storage_path, statusx) VALUES(?,?,?,?,?)",
                   (item2search, returned_name, 0, self.storage_path, "Starting..."))
            self.get_video_thread(item2search)
        elif not self.is_file_downloaded(item2search):
            # if video has not been downloaded and marked complete in DB
            update("UPDATE videos SET statusx=?", ("Restarting...",))
            self.get_video_thread(item2search)
        else:
            self.alert("File already downloaded")

    def on_error(self, returned_error, item2search):
        """
        When an error occurs, This is called. we just update the status bar for nwo

               Args:
                   ret: the error message
                   item2search: What was searched
               Returns:
                   None

        """
        self.setStatusTip(returned_error)

    def on_status(self, returned_status, item2search):
        """
        When the commandline returns a status message, this gets called from the download thread

               Args:
                   returned_status: The status message where we get that progressbar data from
                   item2search: The item being searched
               Returns:
                   None

        """
        self.setStatusTip("")
        matches = self.main_ui.videoTreeW.findItems(item2search,QtCore.Qt.MatchFlag(), 4)
        size = re.findall(r'(\d+\.\d+%|\d+\.\d+GiB|\d+\.\d+MiB|\d+\.\d+KiB)', returned_status)

        extractedSize = None
        if size:
            extractedSize = size[0]
            # only set the size first index is NOT d%
            if size[0][-1:] == "%":
                matches[0].setText(1, size[1])
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
        returned_status = re.sub("\[youtube\]\s[-_a-zA-Z0-9]{11}:\s", "", returned_status)
        returned_status = re.sub("\[download\]\sDestination:\s", "Destination:", returned_status)
        returned_status = re.sub("\[download\]\s+", "", returned_status)
        returned_status = re.sub("\[ffmpeg\]\s", "", returned_status)

        if re.match(r"^(Deleting\soriginal\sfile|Not\sconverting\svideo\sfile\s)", returned_status):
            returned_status = "Download complete"

        if extractedSize is not None:
            params = (self.storage_path, returned_status, extractedSize, item2search,)
            update("update videos set storage_path=?, statusx=?, sizex=? where video_id=?", params)
        else:
            # skip size
            params = (self.storage_path, returned_status, item2search,)
            update("update videos set storage_path=?, statusx=? where video_id=?", params)

    def load_storage_path(self):
        """
        This fetches the storage path from the database and save to the class attribute self.storage_path

               Args:
                   None: No argument required exceopt the default self
               Returns:
                   None

        """
        data = select("select value from settings where name='storage_path'").fetchone()
        if data[0] != "":
            self.storage_path = data[0] + "\\"
        else:
            self.storage_path = ""

    def load_videos(self):
        """
        Will load the videos and pass it to the method that populates the QTreeWidget
            QTreeWidget gets populated at different places.

               Args:
                   None: No argument required exceopt the default self
               Returns:
                   None

        """
        data = select("SELECT id, video_id, namex, sizex, datesx, storage_path, "
                      "statusx FROM videos ORDER BY id DESC limit 100").fetchall()
        self.main_ui.videoTreeW.clear()
        self.populate_tree_widget(data)
        self.main_ui.videoTreeW.setColumnHidden(4, True)
        self.main_ui.videoTreeW.setColumnHidden(5, True)
        self.main_ui.videoTreeW.setColumnHidden(6, True)
        self.main_ui.videoTreeW.setColumnHidden(7, True)

    def open_file(self, twi, indx):
        """
        Attempts to play the downloaded movie with the system's default player

               Args:
                   twi: TreeWidgetItem where the download link will be extracted from
                   indx: the column clicked, passed in from the doubleclick event but unneeded
               Returns:
                   None

        """
        os.startfile(twi.text(6) + twi.text(0) + "_" + twi.text(4) + ".mp4")

    def search_database(self, searchText):
        """
        When users have many downloaded videos and need to search for a specific one
            the search bar emits a signal that calls this everytime the text changes.
             this can be improved

               Args:
                   searchText: The text the user typed in
               Returns:
                   None

        """
        data = select("SELECT id, video_id, namex, sizex, datesx, storage_path, statusx FROM videos "
                      "WHERE namex like ? ORDER BY id DESC", ("%"+searchText+"%",)).fetchall()
        self.main_ui.videoTreeW.clear()
        self.populate_tree_widget(data)

    def populate_tree_widget(self, data):
        """
        It populates the QTreeWidget without worrying about all the checks


               Args:
                   data: List of video data to insert to QTreeWidget
               Returns:
                   None

        """
        for x in data:
            item = QtGui.QTreeWidgetItem(self.main_ui.videoTreeW)
            item.setText(0, str(x[2]))
            item.setText(1, str(x[3]))
            item.setText(3, str(x[4]))
            item.setText(4, str(x[1]))
            item.setText(5, str(x[0]))
            item.setText(6, str(x[5]))
            # create placeholder widget so we can resize widget and not progressbar itself
            progressBarBG = QtGui.QWidget(self.main_ui.videoTreeW)
            # create progressbar and assign parent
            downloadProgressBar = QtGui.QProgressBar(progressBarBG)
            downloadProgressBar.setGeometry(QtCore.QRect(4, 2, 300, 14))
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