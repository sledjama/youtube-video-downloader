
from PyQt4 import QtCore
from functions import *
import subprocess

    

class backgroundProcess(QtCore.QThread):
    
    def __init__(self,cmd, youtubeLink, what2do):
        QtCore.QThread.__init__(self)
        self.cmd=cmd
        self.youtubeLink=youtubeLink
        self.what2do=what2do
        
    def __del__(self):
        self.wait()

        
    def run(self):
        processLink=self.cmd+" --no-check-certificate -f mp4/bestvideo "+self.youtubeLink
        #add --verbose to get full authenticated path to video
        ret=subprocess.Popen(processLink, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)#os.system("youtube-dl.exe -e "+ytLink)

        for line in ret.stdout:
            if self.what2do=="get_name":
                self.emit(QtCore.SIGNAL('nameReady(const QString&, const QString&)'), str(line,"utf-8").strip(),self.youtubeLink)
            elif self.what2do=="download_video":
                self.emit(QtCore.SIGNAL('statusReady(const QString&, const QString&)'), str(line,"utf-8").strip(),self.youtubeLink)

        for err in ret.stderr:
            self.emit(QtCore.SIGNAL('errorReady(const QString&, const QString&)'), str(err,"utf-8").strip(),self.youtubeLink)

            


                
