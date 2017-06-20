import re
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import datetime
import os
import pymysql
import types
from pylab import *
import wx

mpl.rcParams['font.sans-serif'] = ['SimHei'] #指定默认字体
mpl.rcParams['axes.unicode_minus'] = False #解决保存图像是负号'-'显示为方块的问题

def get_txtfile():#获得当前文件夹下所有txt格式文件并返回
    file = []
    for filename in os.listdir():
        if (filename[-3:] == 'txt'):
            print(filename)
            file.append(filename)
    return file


def add(ele,Sum):#累计同一时间下数目
    if(ele in Sum):
        Sum[ele]=Sum[ele]+1
    else :Sum[ele]=1

def data_process(filename,sql,acount):#分为数据获取，与数据输出

    day,hour=data_time(filename=filename,sql=sql,acount=acount)
    output_time(filename[0:-4],day,hour)


def output_time(filename,day,hour):#包含日期与时间的输出
    output_hour(hour,filename=filename)
    output_day(day,filename=filename)

def data_time(filename,sql,acount):#数据获取与存储的主函数
    text = open(filename, 'r', encoding='utf-8')
    content = text.readlines()

    Years = {}
    Months = {}
    Days = {}
    Time_hours = {}
    Data_for_sql=[]
    for i in range(len(content)):
        time_line = content[i]
        date = re.match(r'^(\d{4})-(\d{2})-(\d{2})', time_line)
        time = re.search(r'(\d{2}):(\d{2}):(\d{2})', time_line)
        if (date != None and time != None):

            date = date.group(0)
            time = time.group(0)
            if (sql == 1):
                username = time_line[20:-1]
                text= content[i + 1]
                text=text[0:-1]

                year=date[0:4]
                month=date[5:7]
                day=date[8:10]

                hour=time[0:2]
                minute=time[3:5]
                second=time[6:8]

                data_for_sql=[year,month,day,hour,minute,second,username,text]
                Data_for_sql.append(data_for_sql)


            day = date
            time_hour = time[0:2]

            add(day, Days)
            add(time_hour, Time_hours)
    if(sql==1):
        data2mysql(Data_for_sql,filename[0:-4],acount=acount)#若sql参数为1，则调用，将数据存储入本地mysql
    return Days,Time_hours

def output_hour(hours,filename):
    data_key, data_value = sort_key(hours)
    histogram_2list(data_key, data_value, 'hour',filename)


def output_day(days,filename):
    data_key,data_value=sort_key(days)
    histogram_2list(data_key,data_value,'day',filename)

def sort_key(dic):#将dictionary拆分为两个list，进行排序并返回
    keys=[]
    for key in dic.keys():
        keys.append(key)
    list_key=[]
    list_value=[]
    while(keys!=[]):
        key_min=min(keys)
        list_key.append(key_min)
        list_value.append(dic[key_min])
        keys.remove(key_min)
    return list_key,list_value

def zero_insert(list_key,list_value):#对于没有数据记录的日期实现插0处理
    Date=[]
    for key in list_key:
        date=datetime.datetime(year=int(key[0:4]),month=int(key[5:7]),day=int(key[8:10]))
        Date.append(date)
    now=Date[0]
    delta=datetime.timedelta(days=1)
    i=0
    while (Date[i]!=Date[-1]):
        now=now+delta
        i=i+1
        if(Date[i]==now):
            continue
        else:
            Date.insert(i,now)
            list_value.insert(i,0)
    return Date,list_value

def histogram_2list(X,Y,mode,filename):#对处理好的数据进行绘图输出，并保存与当前文件夹下

    if(mode=='day'):
        plt.figure()
        X, Y = zero_insert(X, Y)
        plt.xlabel(mode + ' since ' + str(X[0])+' to '+str(X[-1]))
        plt.axis([0,len(X)+1, 0, max(Y) * 1.1])
    if(mode=='hour'):
        plt.figure()
        plt.xlabel('24hours')
        plt.axis([0, 24, 0, max(Y)*1.1])
    XX=range(len(X))
    plt.ylabel('sum')
    plt.title(mode+' of '+filename)
    H= plt.bar(left=XX,height=Y,width=1,color='green',align='center')
    if(mode=='hour'):
        autolabel(H)
    plt.savefig(filename+'_'+mode+'.jpg')

def autolabel(rects):#为图中添加坐标值
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x()+rect.get_width()/2., 1.03*height, '%s' % float(height))

def data_process_all(sql):#调用data_process处理所有get_txtfile返回的当前目录下文件
    acount=None
    if(sql):
        if(input('Using default acount? ')):
            acount=['localhost','root','tuihongshiyu','qq_data']
        else:
            print('Input the host,user,password,database separately')
            host = input('host: ')
            user = input('user: ')
            password = input('password: ')
            database = input('database: ')
            account = [host, user, password, database]


    print('DATA PROCESSING BEGIN.')
    files=get_txtfile()
    if(files!=None):
        print(files)
        for file in files:
            data_process(file,sql=sql,acount=acount)

        S=input('Showing the picture or not? ')
        if(S==1):
           plt.show()
    else: print('No file can be found!')
    print('DATA PROCESSING ERROR.')



def data2mysql(DATA,filename,acount):#将数据存储入本地的mysql,若出现编码错误，则忽略该条，同名文件会覆盖从前的数据库

    host=acount[0]
    user=acount[1]
    password=acount[2]
    database=acount[3]



    try:
        db=pymysql.connect(host,user,password,database,charset='utf8')
    except:
        print('CONNECTING ERROR')
    cursor=db.cursor()
    cursor.execute("DROP TABLE IF EXISTS "+filename)
    sql1 = """CREATE TABLE """
        sql2 = """ (
    year smallint,
    month tinyint,
    day tinyint,
    hour tinyint,
    minute tinyint,
    second tinyint,
    user_name tinytext,
    text text
    )character SET=utf8;"""
    sql = sql1 + filename + sql2
    cursor.execute(sql)

    for data in DATA:
        sql = "insert into "+filename+"""
        values("""
        for value in data:
            if (value == data[-1] or value == data[-2]):
                value = punctuation_trans(value)
                value = '"' + value + '"'
            sql=sql+str(value)+','
        sql=sql[0:-1]+');'
        try:
            cursor.execute(sql)
        except:
            print(sql,'\nILLEGAL TEXT')
            continue

    db.commit()
    db.close()

def punctuation_trans(str):#字符转义，便于sql储存
    str=str.replace("。",".")
    str =str.replace("，",",")
    str = str.replace("“", " ")
    str = str.replace("”", " ")
    str = str.replace("\"", " ")
    str = str.replace("\\", " ")
    return str

def interface():#简单交互界面
    app=wx.App()
    win=wx.Frame(None,title='QQdata_process',size=(370,110))
    Button_processall=wx.Button(win,label='Process all with sql',size=(160,50),pos=(10,10))
    Button_processall.Bind(wx.EVT_BUTTON,deal_with_sql)
    Button_process_nosql=wx.Button(win,label='Process without sql',size=(160,50),pos=(180,10))
    Button_process_nosql.Bind(wx.EVT_BUTTON, deal_without_sql)
    win.Show()

    app.MainLoop()
def deal_with_sql(event):
    data_process_all(sql=1)
def deal_without_sql(event):
    data_process_all(sql=0)

# data_process('.txt')#单个文件操作，一般用于调试。
# data_process_all()
interface()