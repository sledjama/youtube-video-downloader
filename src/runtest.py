import unittest, sys
import tests.all_tests
testSuite = tests.all_tests.create_test_suite()
print("###############")
text_runner = unittest.TextTestRunner().run(testSuite)
print(text_runner)
sys.exit(-1)