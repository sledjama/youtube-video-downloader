import unittest
import os, sys
from functools import reduce
from mock import Mock
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from PyQt4 import QtGui, QtCore, QtTest

from functions import *
from Downloader import *
from _version import __version__
import configs, os

cwd = os.getcwd()
sys.path.insert(0, cwd)

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
        self.assertEqual(self.ytd.windowTitle(),  "Youtube Downloader - "+__version__ )

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
            matches=self.ytd.main_ui.videoTreeW.findItems(v,QtCore.Qt.MatchExactly,4)
            self.assertEqual(len(matches),1)
            self.assertEqual(v, matches[0].text(4))

    def test_populateTreeWidget(self):
        #test that treewidget gets populated, it takes a tuple of lists in this order
        #id, video_id, namex, sizex, datesx, storage_path, statusx
        lam=lambda x, y: x + y
        inputData=([ '1',  'V6JcxAN5kXs', 'Test video name', '30MiB', '2017-11-05 00:04:00','downloads', 'Download complete' ],[ '2',  'u6JcxAN5kXt', 'Test video name 2', '47MiB', '2017-11-05 00:04:00','downloads', 'Download complete' ])
        expectedResult="Test video name 247MiB2017-11-05 00:04:00u6JcxAN5kXt2downloadsTest video name30MiB2017-11-05 00:04:00V6JcxAN5kXs1downloads"
        self.ytd.populateTreeWidget(inputData)
        sr=self.ytd.main_ui.videoTreeW.findItems("2017-11-05 00:04:00",QtCore.Qt.MatchExactly,3)
        result=reduce(lam, [reduce(lam,[x.text(0), x.text(1), x.text(2), x.text(3), x.text(4), x.text(5), x.text(6)]) for x in sr])
        self.assertEqual(expectedResult, result)

    def test_searchDB(self):
        self.initDB()
        self.ytd.searchDB("Test searchDB name")
        sr = self.ytd.main_ui.videoTreeW.findItems("QuhTEST9ui2", QtCore.Qt.MatchExactly, 4)
        self.assertEqual(sr[0].text(3), '2017-11-05 00:04:00')
        #cleanup DB for next test
        delete("DELETE FROM videos WHERE id=?",(self.dbid,))

    def test_loadVideos(self):
        self.initDB()
        self.ytd.loadVideos()
        sr = self.ytd.main_ui.videoTreeW.findItems("QuhTEST9ui2", QtCore.Qt.MatchExactly, 4)
        self.assertEqual(sr[0].text(3), '2017-11-05 00:04:00')
        #cleanup DB for next test
        delete("DELETE FROM videos WHERE id=?",(self.dbid,))



    def initDB(self):
        #needed for multiple test methods
        self.dbid = '2323'
        delete("DELETE FROM videos WHERE id=?", (self.dbid,))
        insert("INSERT INTO videos (id, video_id, namex, sizex, datesx,storage_path, statusx) VALUES(?,?,?,?,?,?,?)",
               (self.dbid, 'QuhTEST9ui2', 'Test searchDB name', '30MiB', '2017-11-05 00:04:00', 'downloads', 'Download complete'))


if __name__ == "__main__":
    unittest.main()
