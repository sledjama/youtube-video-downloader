import os

print ("compiling UIs")
os.system("pyuic4 ui/ui/main.ui > ui/py/ui_main.py")
os.system("pyuic4 ui/ui/pref.ui > ui/py/ui_pref.py")
#os.system("pyrcc4 resources.qrc > resources_rc.py -py3")

print ("completed")