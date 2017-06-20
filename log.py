import time
import os

def get_time():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def log_print(sentence):
    log=get_time()+' '+str(sentence)
    print(log)
    return log

def log_write(sentence,path,name):
    path = path + 'Log of ' + str(name) + '.txt'
    log=get_time()+str(sentence)+'\n'

    if not os.path.exists(path):
        f = open(path, 'w')
        f.close()
    else:
        # os.remove(path)
        f_w = open(path, 'a')
        f_w.write(log)
        f_w.close()
