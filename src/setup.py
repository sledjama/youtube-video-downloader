
from cx_Freeze import setup, Executable
import sys
import os
import zipfile
################################



exe = Executable(
    script="main.py",
    icon="images/logo.ico",
    base="Win32GUI",

    compress=False
    )
    #
    #base="Win32GUI",


buildOptions = dict(
        excludes = ["tkinter"], append_script_to_exe = ['main.exe.manifest'])


setup(
        name = "YoutubeDownloader",
        version = "0.1",
        description = "Download youtube videos",
        executables = [exe],
        options = dict(build_exe = buildOptions))

