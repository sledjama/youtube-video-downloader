"""
I found this helpful script here
https://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure
"""
import glob
import unittest, os

def create_test_suite():
    test_file_strings = glob.glob(os.path.join('tests','test_*.py'))
    module_strings = ['tests.'+stri[6:len(stri)-3] for stri in test_file_strings]
    suites = [unittest.defaultTestLoader.loadTestsFromName(name) for name in module_strings]
    testSuite = unittest.TestSuite(suites)
    return testSuite