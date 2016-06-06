import os

print ("compiling UIs")
os.system("pyuic4 main.ui > ui_main.py")
os.system("pyuic4 pref.ui > ui_pref.py")
#os.system("pyrcc4 resources.qrc > resources_rc.py -py3")

print ("completed")