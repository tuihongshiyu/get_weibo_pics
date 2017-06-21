import types
import time
import re
import os
import datetime


def str2dic(str):
    str = str.replace("true", '1')
    str = str.replace("false", '0')
    str = str.replace("null", '0')
    pat = re.compile(r'<([^<>]*)>')
    str = pat.sub('', str)
    try:
        dic = eval(str)
    except:
        str = str.replace(",\"", '\n\"')
        pat = re.compile(r'/"([^/"]*)"')
        str = pat.sub('', str)
        return 'Error'
    return dic


def is_num_by_except(str):
    try:
        int(str)
        return True
    except:
        return False


def get_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


def sinatime2format(sina_time):
    ch = sina_time[0:2]
    if (sina_time[0:2] == '今天'):
        time = (get_time('today')) + sina_time[-6:]
    elif (sina_time[0:2] == '昨天'):
        time = get_time('yesterday') + sina_time[-6:]
    elif (len(sina_time) == 11):
        time = (get_time())[0:5] + sina_time
    else:
        time = sina_time
    return time


def datetime2mysql(time):
    time = time.replace(':', '')
    time = time.replace('-', '')
    time = time.replace(' ', '')
    if (len(time) != 14):
        return time + '00'
    else:
        return time
