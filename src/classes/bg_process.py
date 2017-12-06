"""
This is a background process thread that helps keep the UI usable,
it starts the commandline process and waits for responses.
It emits signals to the main UI which get used for the progressbar
displays.
The actual job of figuring what to download, how many threads to use etc.
 has really been outsourced to youtube-dl
"""
from PyQt4 import QtCore
from functions import *
import subprocess

class BackgroundProcess(QtCore.QThread):
    def __init__(self, cmd, youtube_link, what2do):
        """
        setup the Qthread class and sets commands to this instance
        :param cmd:  The command to run
        :param youtube_link: The youtube link to process
        :param what2do: lets thread know whether to fetch just the video name only
                        or download video
        """
        QtCore.QThread.__init__(self)
        self.cmd = cmd
        self.youtube_link = youtube_link
        self.what2do = what2do
        
    def __del__(self):
        """
        this gets called when running download thread is about to be re-assigned
        it just make the new owner wait
        :return:
        """
        self.wait()

    def run(self):
        """
        For now, we are fetching the best quality video and prefer mp4 if available

        :return:
        """
        process_link = self.cmd + " --no-check-certificate -f mp4/bestvideo " + self.youtube_link
        # add --verbose to get full authenticated path to video
        return_status = subprocess.Popen(process_link, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        for line in return_status.stdout:
            if self.what2do == "get_name":
                self.emit(QtCore.SIGNAL('nameReady(const QString&, const QString&)'),
                          str(line, "utf-8").strip(), self.youtube_link)
            elif self.what2do == "download_video":
                self.emit(QtCore.SIGNAL('statusReady(const QString&, const QString&)'),
                          str(line, "utf-8").strip(), self.youtube_link)

        for err in return_status.stderr:
            self.emit(QtCore.SIGNAL('errorReady(const QString&, const QString&)'),
                      str(err, "utf-8").strip(), self.youtube_link)
