
from cx_Freeze import setup, Executable
import sys

sys.argv.append("build")
#setup main file, icon and export base
exe = Executable(script="test_Downloader.py",icon="images/logo.ico",base="Win32GUI")

#setup options
buildOptions = dict(
        excludes = ["tkinter"],
        includes = ["ui.py"],
        optimize=1
    )

#compile
setup(
        name = "YoutubeDownloader",
        version = "0.2.1",
        description = "Download youtube videos",
        executables = [exe],
        options = dict(build_exe = buildOptions)
    )


