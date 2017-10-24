import unittest
import os, sys
from mock import Mock
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from PyQt4 import QtGui, QtCore, QtTest

from src.Downloader import *

app = QtGui.QApplication(sys.argv)

class TestYoutubeDownloader(unittest.TestCase):

    def setUp(self):
        #buildgui
        self.ytd=YoutubeDownloader()


    def tearDown(self):
        #killgui
        pass

    def test_GUI(self):
        #test that GUI is created
        self.assertEqual(self.ytd.windowTitle(),  "Youtube Downloader - "+version )

    def test_addToQueue(self):
        #test that youtube input form grabs only youtube urls
        self.ytd.thread_getname=Mock(return_value=None)
        sampleLinks={"https://www.youtube.com/watch?v=V6JcxAN5kXs": "V6JcxAN5kXs", \
                     "https://www.youtube.com/watch?list=PL6gx4Cwl9DGAcbMi1sH6oAMk4JHw91mC_": "PL6gx4Cwl9DGAcbMi1sH6oAMk4JHw91mC_",\
                     "V6JcxAN5kXs": "V6JcxAN5kXs", \
                     "PL6gx4Cwl9DGAcbMi1sH6oAMk4JHw91mC_":"PL6gx4Cwl9DGAcbMi1sH6oAMk4JHw91mC_"}

        for k,v in sampleLinks.items():
            self.ytd.main_ui.videoTreeW.clear()
            self.ytd.addToQueue(k)
            matches=self.ytd.main_ui.videoTreeW.findItems(v,QtCore.Qt.MatchFlag(),4)
            self.assertEqual(len(matches),1)
            self.assertEqual(v, matches[0].text(4))

if __name__ == "__main__":
    unittest.main()