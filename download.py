import requests
import urllib.request
from bs4 import BeautifulSoup
import pymysql
import types
import time
import re
import os
import warnings
warnings.filterwarnings("ignore")
from multiprocessing import Pool
import datetime
from .sql import *
from .common import *
host = 'localhost'
user = 'root'
password = 'Tuihongshiyu5'
database = 'weibo_pics'

PIC_PATH = '/Users/HirosueRyouko/Pictures/From Weibo/'
list_path = '/Users/HirosueRyouko/Pictures/From Weibo/ID_LIST.txt'


def download_pic(url, name, user_id, path=PIC_PATH):
    pic = requests.get(url)
    if not os.path.exists(path + user_id):
        os.mkdir(path + user_id)
    if os.path.exists(path + user_id + '/' + name + '.jpg'):
        return True
    # print(path + user_id + '/' + name + '.jpg')
    try:
        f = open(path + user_id + '/' + name + '.jpg', 'wb')
        f.write(pic.content)
        f.close()
        return True
    except:
        return False

def main_download(user_id):
    print('Downloading of ',user_id,' begins')
    sum_download = 0
    sum_failure=0
    pics_info = undownloadedpics(user_id)
    url, id = pics_info['url'], pics_info['id']
    for i in range(len(url)):
        if download_pic(url=url[i], name=id[i], user_id=user_id)==True:
            setpic_downloaded(user_id=user_id, id=id[i])
            sum_download = sum_download + 1
        else:
            sum_failure=sum_failure+1
            None
        # print(sum_download,sum_failure)
    print('Download ' + str(sum_download) + ' pics from ' + user_id)
    print(str(len(url)-sum_download),' pics of '+user_id+' remain undownloaded\n')

def setpic_downloaded(user_id, id):
    try:
        db = pymysql.connect(host, user, password, database, charset='utf8')
        cursor = db.cursor()
        # print('CONNECTING SUCESSFULLY')
    except:
        print('CONNECTING ERROR')
    try:
        sql = "update weibo_pics.user" + user_id + " set downloaded = \'1\' where id =" + "\"" + id + "\";"
        cursor.execute(sql)

    except:
        print("ERROR")
        return False

    db.commit()
    db.close()
    return True
