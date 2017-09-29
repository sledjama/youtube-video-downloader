import os
from PyQt4 import QtNetwork, QtCore, QtGui
from functions import *
import time


class webWorker(QtCore.QThread):

    def __init__(self,d_path, progress=None, grab_resource=None, httpsecure=False, anotherdomain=None, image=False):
        QtCore.QThread.__init__(self)
        
        self.param="exe=1"
        self.d_path=d_path
        self.progress=progress
        self.grab_resource=grab_resource
        self.httpsecure=httpsecure
        self.host=anotherdomain
        self.image=image
        if not self.httpsecure:
            if self.host is not None:
                self.http = QtNetwork.QHttp(self.host)#,QtNetwork.QHttp.ConnectionModeHttps, 443
            else:
                self.http = QtNetwork.QHttp(host)#,QtNetwork.QHttp.ConnectionModeHttps, 443
        else:
            if self.host is not None:
                self.http = QtNetwork.QHttp(self.host, QtNetwork.QHttp.ConnectionModeHttps, 443)
            else:
                self.http = QtNetwork.QHttp(host, QtNetwork.QHttp.ConnectionModeHttps, 443)
        QtCore.QObject.connect(self.http, QtCore.SIGNAL("done(bool)"), self.d_done)
        QtCore.QObject.connect(self.http, QtCore.SIGNAL("dataReadProgress(int, int)"), self.d_progress)
        QtCore.QObject.connect(self.http, QtCore.SIGNAL("sslErrors (const QList<QSslError>&)"), self.sslErr)

    def __del__(self):
        self.wait()

    def sslErr(self,errList):
        self.http.ignoreSslErrors()
        print(errList[0].errorString())
        print(errList[1].errorString())
        
    def run(self):
        ba=QtCore.QByteArray(self.param)
        #if it is image, we use get method since we will be fetching it from the CDN
        if self.image:
            header=QtNetwork.QHttpRequestHeader("GET",self.d_path)
        else:
            header=QtNetwork.QHttpRequestHeader("POST",self.d_path)

        if self.host is not None:
            header.setValue("Host",self.host)
        else:
            header.setValue("Host",host)

        if not self.httpsecure:
            header.setValue("Port","443")
        header.setContentType("application/x-www-form-urlencoded")
        header.setContentLength(ba.length())
        self.http.request(header,ba)



    def d_done(self,status):
        global FleetMasters
        
        if status:
            print("Download error:"+self.http.errorString())
                
        else:
            if self.grab_resource is None:
                data=str(self.http.readAll(),"utf-8")
            else:
                f=open("temp\\"+os.path.basename(self.grab_resource),"wb")
                f.write(self.http.readAll())
                f.close()
                data=os.path.basename(self.grab_resource)
            self.emit(QtCore.SIGNAL('update(QString)'), data)
            if self.progress is not None:
                self.progress.hide()
            
            

    def d_progress(self, a,b):
        if b!=0:
            if self.progress is not None:
                self.progress.show()
            newVal=(a/b)*100
            if self.progress is not None:
                self.progress.setValue(newVal)


                
