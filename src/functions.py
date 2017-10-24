import urllib.parse
from urllib.parse import urlparse, parse_qs
import urllib.request
from urllib.error import HTTPError
from urllib.error import URLError
from PyQt4 import QtNetwork, QtCore
import sqlite3, os

conn = sqlite3.connect(os.path.join('database','db'))
youtubeProgram="programs\youtube-dl.exe"



def callPage(path,params=None):
    
    url = path
    data= None
    if params is not None:
        values=params
        data = urllib.parse.urlencode(values)
        data = data.encode('utf-8')
    try:     
        req = urllib.request.Request(url, data)
        print("calling page...")
        response = urllib.request.urlopen(req)
        the_page = response.read()
        return the_page.decode()
    except HTTPError as e:
        the_page="error:"+e.value
        return the_page.decode()
    except URLError as e:
        the_page="error:"+e.value
        return the_page.decode()


def urlencode(param):
    return urllib.parse.quote_plus(param, safe='', encoding=None, errors=None)


def check2int(obj):
    if obj.isChecked():
        return "1"
    else:
        return "0"

def int2check(obj, intiger):
    if intiger=="1":
        obj.setChecked(True)
    else:
        obj.setChecked(False)


        
def deleteTWI(tree):
    while tree.topLevelItemCount()>0:
        obj=tree.takeTopLevelItem(0)
        del obj


def video_id(value):
    # curled  from http://stackoverflow.com/questions/4356538/how-can-i-extract-video-id-from-youtubes-link-in-python
    #
    #  submitted by Mikhail Kashkin
    # modified by Ajayi seun to return list if exists
    """
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    -https://www.youtube.com/watch?v=cox06WZ6HMI&list=PLKt6aXnD1eKtO_NUn0ImSkxr22VbJHTKA
    """
    query = urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            if "list" in p:
                return p['list'][0]
            elif "v" in p:
                return p['v'][0]
            else:
                return "Invalid!"
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    return value


def createDB():
    global conn
    c = conn.cursor()
    currentWorkingDir=os.getcwd()
    print(currentWorkingDir)
    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS "videos" (id INTEGER PRIMARY KEY AUTOINCREMENT, video_id TEXT, namex TEXT, sizex TEXT, storage_path TEXT, statusx TEXT, datesx TIMESTAMP DEFAULT CURRENT_TIMESTAMP);''')
    c.execute('''CREATE TABLE IF NOT EXISTS "settings" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL, "name" TEXT NOT NULL  UNIQUE , "value" TEXT);''')
    c.execute("INSERT INTO  settings (name, value) SELECT \"storage_path\", \""+currentWorkingDir+"\\downloads\" WHERE NOT EXISTS (SELECT 1 FROM settings WHERE  name=\"storage_path\");")
    conn.commit()
    print("table created")



def insert(q,vals):
    global conn
    c = conn.cursor()
    # run query
    c.execute(q, vals)
    conn.commit()
    return c

def update(q,vals):
    global conn
    c = conn.cursor()
    # run query
    c.execute(q, vals)
    conn.commit()
    print(q)

def delete(q,vals):
    global conn
    c = conn.cursor()
    # run query
    c.execute(q, vals)
    conn.commit()
    print(q)

def select(q,vals=None):
    global conn
    c= conn.cursor()
    if vals is None:
        c.execute(q)
    else:
        c.execute(q, vals)
    print(q)
    return c