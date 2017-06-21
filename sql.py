import pymysql
import types
import time
import re
import os
import warnings
warnings.filterwarnings("ignore")
from .common import *
from get_weibo_pics.download import *
from get_weibo_pics.sql import *
from get_weibo_pics.text_processing import *
import datetime

host = 'localhost'
user = 'root'
password = 'Tuihongshiyu5'
database = 'weibo_pics'

PIC_PATH = '/Users/HirosueRyouko/Pictures/From Weibo/'
list_path = '/Users/HirosueRyouko/Pictures/From Weibo/ID_LIST.txt'


def info_bottom(user_id):
    try:
        db = pymysql.connect(host, user, password, database, charset='utf8')
        cursor = db.cursor()
        # print('CONNECTING SUCESSFULLY')
    except:
        print('CONNECTING ERROR')
    try:
        sql = "select bottom from weibo_pics.users_info where user_id =" + "\"" + user_id + "\";"
        cursor.execute(sql)
        bottom = cursor.fetchall()
        bottom = (list((list(bottom))[0]))[0]
        db.commit()
        db.close()
        return bottom
    except:
        return 0


def undownloadedpics(user_id):
    pics_path = PIC_PATH + user_id + '/'
    pics_info = {}
    url = []
    id = []
    url_id = []
    try:
        db = pymysql.connect(host, user, password, database, charset='utf8')
        cursor = db.cursor()
        # print('CONNECTING SUCESSFULLY')
    except:
        print('CONNECTING ERROR')

    try:
        sql = "select url,id from weibo_pics.user" + user_id + " where downloaded = \'0\';"
        cursor.execute(sql)
        url_id = list(cursor.fetchall())

    except:
        print("ERROR")
    db.commit()
    db.close()
    for data in url_id:
        data = list(data)
        url.append(data[0])
        id.append(data[1])
    pics_info['url'] = url
    pics_info['id'] = id
    return pics_info


def setinfo_downloaded(user_id):
    try:
        db = pymysql.connect(host, user, password, database, charset='utf8')
        cursor = db.cursor()
        # print('CONNECTING SUCESSFULLY')
    except:
        print('CONNECTING ERROR')
    try:
        sql = "update weibo_pics.users_info set bottom = \'1\' where user_id =" + "\"" + user_id + "\";"
        cursor.execute(sql)

    except:
        print("ERROR TO SET BOTTOM")
        return False

    db.commit()
    db.close()
    return True


def downloaded2mysql(user_id):
    sum_downloaded = 0
    pics_path = PIC_PATH + user_id + '/'
    pic_ids = os.listdir(pics_path)
    try:
        db = pymysql.connect(host, user, password, database, charset='utf8')
        cursor = db.cursor()
        # print('CONNECTING SUCESSFULLY')
    except:
        print('CONNECTING ERROR')
    for pic_id in pic_ids:
        id = pic_id[0:-4]
        try:
            sql = "update weibo_pics.user" + user_id + " set downloaded = \'1\' where id =" + "\"" + id + "\";"
            cursor.execute(sql)
            sum_downloaded = sum_downloaded + 1

        except:
            print("ERROR")
    db.commit()
    db.close()
    print('Downloaded pics: ' + str(sum_downloaded) + ' from ' + user_id)

    # print(pics)
def latest_pic_createat(user_id):
    user_id = 'user' + user_id
    pic_ids = []
    try:
        db = pymysql.connect(host, user, password, database, charset='utf8')
        cursor = db.cursor()
        # print('CONNECTING SUCESSFULLY')
    except:
        print('CONNECTING ERROR')
    try:
        sql = "select createat from weibo_pics." + user_id + " order by createat desc limit 1;"
        cursor.execute(sql)
        # data = list(cursor.fetchall())
        # for pic_info in data:
        #     pic_id = (list(pic_info))[0]
        #     pic_ids.append(pic_id)
        # return pic_ids
        createat=list(cursor.fetchall())[0][0]
        return createat

    except:
        print('select error')
        return None

def get_containerid(user_id='5416247360'):
    try:
        db = pymysql.connect(host, user, password, database, charset='utf8')
        cursor = db.cursor()
        # print('CONNECTING SUCESSFULLY')
    except:
        print('CONNECTING ERROR')
    try:
        sql='select container_id from weibo_pics.users_info where user_id = \"'+user_id+'\";'
        cursor.execute(sql)
        container_id=(list(cursor.fetchall()))[0][0]
    except:
        None
    if container_id==None or 'None':
        url = 'http://m.weibo.cn/container/getIndex?type=uid&value=' + user_id
        page = requests.get(url)
        soup = str(BeautifulSoup(page.text, 'lxml'))
        soup_str = soup[15:-18]
        soup_dic = str2dic(soup_str)
        container_id=soup_dic['tabsInfo']['tabs'][1]['containerid']
        sql = "update weibo_pics.users_info set container_id = \""+str(container_id)+"\" where user_id =\"" + user_id + "\";"
        cursor.execute(sql)
        db.commit()
        db.close()
        return container_id
    else:
        return container_id
def info2mysql(info):  # 将数据存储入本地的mysql,若出现编码错误，则忽略该条，同名文件会覆盖从前的数据库
    sum_insert = 0
    user_id = 'user' + info['user_id']
    Urls = info['url']
    Id = info['id']
    Createat = info['createat']

    try:
        db = pymysql.connect(host, user, password, database, charset='utf8')
        # print('CONNECTING SUCESSFULLY')
    except:
        print('CONNECTING ERROR')
    cursor = db.cursor()
    try:
        cursor.execute("show tables" + ';')
        tables = cursor.fetchall()
        if tables == {} or (user_id,) not in cursor.fetchall():
            sql1 = """CREATE TABLE """
            sql2 = """ (
                    createat datetime,
                    url char(100) NOT NULL,
                    id char(50),
                    downloaded bool,
                    primary key (url)
                    )character SET=utf8;"""
            sql = sql1 + user_id + sql2
            cursor.execute(sql)
        else:
            None

    except:
        None

    for i in range(len(Urls)):
        sql = "insert ignore into " + user_id + """
        values("""
        createat = datetime2mysql(Createat[i])

        sql = sql + createat + ',\"' + Urls[i] + '\",' + '\"' + str(Id[i]) + '\",' + '0' + ');'
        try:
            cursor.execute(sql)
            sum_insert = sum_insert + 1
        except:
            # print(sql, '\nILLEGAL TEXT')
            continue

    db.commit()
    db.close()
    # print('Insert ' + str(sum_insert) + ' pics into ' + info['user_id'])
def user_add(user_id):
    try:
        db = pymysql.connect(host, user, password, database, charset='utf8')
        cursor = db.cursor()
        # print('CONNECTING SUCESSFULLY')
    except:
        print('CONNECTING ERROR')
    try:
        sql="insert into weibo_pics.users_info values(\'"+user_id+"\',\'0\',\'None\',\'None\'"
        cursor.execute(sql)
        db.commit()
        db.close()
    except:
        return None




def users_info():
    user_info = []

    try:
        db = pymysql.connect(host, user, password, database, charset='utf8')
        cursor = db.cursor()
        # print('CONNECTING SUCESSFULLY')
    except:
        print('CONNECTING ERROR')

    try:
        sql = "select * from users_info;"
        cursor.execute(sql)
        users_list = list(cursor.fetchall())
        for user_id in users_list:
            user_id = (list(user_id))[0]
            user_info.append(user_id)

    except:
        return None

    db.commit()
    db.close()
    return user_info

