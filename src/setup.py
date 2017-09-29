
from cx_Freeze import setup, Executable
import sys
import os
import zipfile
################################

sys.argv.append("build")

exe = Executable(
    script="main.py",
    icon="images/logo.ico",
    base="Win32GUI"
    )
    #
    #base="Win32GUI",


buildOptions = dict(
        excludes = ["tkinter"],
        includes = ["ui.py"],
        optimize=1)


setup(
        name = "YoutubeDownloader",
        version = "0.1",
        description = "Download youtube videos",
        executables = [exe],
        options = dict(build_exe = buildOptions))

