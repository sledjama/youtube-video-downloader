db_folder='database'
db_file='db'
youtubeProgram="programs\youtube-dl.exe"
icon_path=':/images/logo.png'


import os, sqlite3
#create path if it does not exist
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

#create database
db_path=os.path.join(db_folder,db_file)
conn = sqlite3.connect(db_path)
