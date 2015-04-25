import os
from PyQt4 import QtNetwork, QtCore, QtGui
from functions import *
import subprocess
import time

    

class backgroundProcess(QtCore.QThread):
    
    def __init__(self,cmd, youtubeLink, what2do):
        QtCore.QThread.__init__(self)
        self.cmd=cmd
        self.youtubeLink=youtubeLink
        self.what2do=what2do
        
    def __del__(self):
        self.wait()

        
    def run(self):
        ret=subprocess.Popen(self.cmd+self.youtubeLink, stdout=subprocess.PIPE)#os.system("youtube-dl.exe -e "+ytLink)

        with ret.stdout as f:
            if self.what2do=="get_name":
                self.emit(QtCore.SIGNAL('nameReady(const QString&, const QString&)'), str(f.read(),"utf-8").strip(),self.youtubeLink)
            elif self.what2do=="download_video":
                self.emit(QtCore.SIGNAL('statusReady(const QString&, const QString&)'), str(f.read(),"utf-8").strip(),self.youtubeLink)



            


                
