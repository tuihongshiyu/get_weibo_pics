import requestsimport urllib.requestfrom bs4 import BeautifulSoupimport pymysqlimport typesimport timeimport reimport osimport warningswarnings.filterwarnings("ignore")from multiprocessing import Poolimport datetimehost = 'localhost'user = 'root'password = 'Tuihongshiyu5'database = 'weibo_pics'PIC_PATH = '/Users/HirosueRyouko/Pictures/From Weibo/'list_path = '/Users/HirosueRyouko/Pictures/From Weibo/ID_LIST.txt'def show_picpath():    print('PIC_PATH: ', PIC_PATH)def set_picpath(PIC_PATH_new):    PIC_PATH = str(PIC_PATH_new)    show_picpath()def error_test(user_id, test_page):    picsinfo2localmysql(user_id, test_page)def get_time():    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))def download_pic(url, name, user_id, path=PIC_PATH):    pic = requests.get(url)    if not os.path.exists(path + user_id):        os.mkdir(path + user_id)    if os.path.exists(path + user_id + '/' + name + '.jpg'):        return True    # print(path + user_id + '/' + name + '.jpg')    try:        f = open(path + user_id + '/' + name + '.jpg', 'wb')        f.write(pic.content)        f.close()        return True    except:        return Falsedef main(user_id):    picsinfo2localmysql(user_id=user_id)    main_download(user_id=user_id)def picsinfo2localmysql(user_id='5416247360', page_begin=1, path=PIC_PATH):    containerid = get_containerid(user_id)    page_no = page_begin    sum_error = 0    bottom = int(info_bottom(user_id=user_id))    headers = {        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'    }    while (True):        url = 'http://m.weibo.cn/container/getIndex?type=uid&value=' + user_id + '&containerid=' + containerid + '&page=' + str(            page_no)        page = requests.get(url, headers=headers)        soup_dic = str2dic(str(BeautifulSoup(page.text, 'lxml')))        if soup_dic == 'Error' or soup_dic['cards'] == []:            sum_error = sum_error + 1            if (sum_error >= 7):                setinfo_downloaded(user_id)                print('Done in page ', str(page), ' of ', user_id)                return            page_no = page_no + 1        else:            sum_error=0            pics_info, top_info = get_dic_info(soup_dic)            pics_info['user_id'] = user_id            # print('id : ', user_id, ' Page: ', pics_info['page'], ' Num of urls: ', len(pics_info['url']))            info2mysql(pics_info)            if nextpage(user_id, pics_info['createat']) == False:                if (bottom == 1):                    print('No next page for ',user_id)                    return                else:                    None            else:                print('So next the page of '+str(page_no)+' for ', user_id)                page_no = page_no + 1                time.sleep(0.5)def main_download(user_id):    print('Downloading of ',user_id,' begins')    sum_download = 0    sum_failure=0    pics_info = undownloadedpics(user_id)    url, id = pics_info['url'], pics_info['id']    for i in range(len(url)):        if download_pic(url=url[i], name=id[i], user_id=user_id)==True:            setpic_downloaded(user_id=user_id, id=id[i])            sum_download = sum_download + 1        else:            sum_failure=sum_failure+1            None        # print(sum_download,sum_failure)    print('Download ' + str(sum_download) + ' pics from ' + user_id)    print(str(len(url)-sum_download),' pics of '+user_id+' remain undownloaded\n')def setpic_downloaded(user_id, id):    try:        db = pymysql.connect(host, user, password, database, charset='utf8')        cursor = db.cursor()        # print('CONNECTING SUCESSFULLY')    except:        print('CONNECTING ERROR')    try:        sql = "update weibo_pics.user" + user_id + " set downloaded = \'1\' where id =" + "\"" + id + "\";"        cursor.execute(sql)    except:        print("ERROR")        return False    db.commit()    db.close()    return Truedef info_bottom(user_id):    try:        db = pymysql.connect(host, user, password, database, charset='utf8')        cursor = db.cursor()        # print('CONNECTING SUCESSFULLY')    except:        print('CONNECTING ERROR')    try:        sql = "select bottom from weibo_pics.users_info where user_id =" + "\"" + user_id + "\";"        cursor.execute(sql)        bottom = cursor.fetchall()        bottom = (list((list(bottom))[0]))[0]        db.commit()        db.close()        return bottom    except:        return 0def setinfo_downloaded(user_id):    try:        db = pymysql.connect(host, user, password, database, charset='utf8')        cursor = db.cursor()        # print('CONNECTING SUCESSFULLY')    except:        print('CONNECTING ERROR')    try:        sql = "update weibo_pics.users_info set bottom = \'1\' where user_id =" + "\"" + user_id + "\";"        cursor.execute(sql)    except:        print("ERROR TO SET BOTTOM")        return False    db.commit()    db.close()    return Truedef undownloadedpics(user_id):    pics_path = PIC_PATH + user_id + '/'    pics_info = {}    url = []    id = []    url_id = []    try:        db = pymysql.connect(host, user, password, database, charset='utf8')        cursor = db.cursor()        # print('CONNECTING SUCESSFULLY')    except:        print('CONNECTING ERROR')    try:        sql = "select url,id from weibo_pics.user" + user_id + " where downloaded = \'0\';"        cursor.execute(sql)        url_id = list(cursor.fetchall())    except:        print("ERROR")    db.commit()    db.close()    for data in url_id:        data = list(data)        url.append(data[0])        id.append(data[1])    pics_info['url'] = url    pics_info['id'] = id    return pics_infodef downloaded2mysql(user_id):    sum_downloaded = 0    pics_path = PIC_PATH + user_id + '/'    pic_ids = os.listdir(pics_path)    try:        db = pymysql.connect(host, user, password, database, charset='utf8')        cursor = db.cursor()        # print('CONNECTING SUCESSFULLY')    except:        print('CONNECTING ERROR')    for pic_id in pic_ids:        id = pic_id[0:-4]        try:            sql = "update weibo_pics.user" + user_id + " set downloaded = \'1\' where id =" + "\"" + id + "\";"            cursor.execute(sql)            sum_downloaded = sum_downloaded + 1        except:            print("ERROR")    db.commit()    db.close()    print('Downloaded pics: ' + str(sum_downloaded) + ' from ' + user_id)    # print(pics)def nextpage(user_id, createat):    creatat_latest = latest_pic_createat(user_id)    for i in range(len(createat)):        str_time_latest=creatat_latest.strftime('%Y-%m-%d %H:%M')        if str_time_latest > createat[i]:            return False        else:            None    return Truedef latest_pic_createat(user_id):    user_id = 'user' + user_id    pic_ids = []    try:        db = pymysql.connect(host, user, password, database, charset='utf8')        cursor = db.cursor()        # print('CONNECTING SUCESSFULLY')    except:        print('CONNECTING ERROR')    try:        sql = "select createat from weibo_pics." + user_id + " order by createat desc limit 1;"        cursor.execute(sql)        # data = list(cursor.fetchall())        # for pic_info in data:        #     pic_id = (list(pic_info))[0]        #     pic_ids.append(pic_id)        # return pic_ids        createat=list(cursor.fetchall())[0][0]        return createat    except:        print('select error')        return Nonedef get_containerid(user_id='5416247360'):    try:        db = pymysql.connect(host, user, password, database, charset='utf8')        cursor = db.cursor()        # print('CONNECTING SUCESSFULLY')    except:        print('CONNECTING ERROR')    try:        sql='select container_id from weibo_pics.users_info where user_id = \"'+user_id+'\";'        cursor.execute(sql)        container_id=(list(cursor.fetchall()))[0][0]    except:        None    if container_id==None or 'None':        url = 'http://m.weibo.cn/container/getIndex?type=uid&value=' + user_id        page = requests.get(url)        soup = str(BeautifulSoup(page.text, 'lxml'))        soup_str = soup[15:-18]        soup_dic = str2dic(soup_str)        container_id=soup_dic['tabsInfo']['tabs'][1]['containerid']        sql = "update weibo_pics.users_info set container_id = \""+str(container_id)+"\" where user_id =\"" + user_id + "\";"        cursor.execute(sql)        db.commit()        db.close()        return container_id    else:        return container_iddef str2dic(str):    str = str.replace("true", '1')    str = str.replace("false", '0')    str = str.replace("null", '0')    pat = re.compile(r'<([^<>]*)>')    str = pat.sub('', str)    try:        dic = eval(str)    except:        str = str.replace(",\"", '\n\"')        pat = re.compile(r'/"([^/"]*)"')        str = pat.sub('', str)        return 'Error'    return dicdef get_dic_info(dic):    time = ''    page_info = {}    top_info = {'is_top': 0, 'num_top': 0}    page_info['page'] = dic['cardlistInfo']['page']    page_info['url'] = {}    page_info['id'] = {}    page_info['createat'] = {}    num = 0    num2 = 0    for i in range(len(dic['cards'])):        try:            card = dic['cards'][i]['mblog']            card_str = str(dic['cards'][i]['mblog'])            createat = sinatime2format(card['created_at'])            page_info['url'][num] = (card['original_pic']).replace('\\', '')            page_info['id'][num] = card['id']            page_info['createat'][num] = createat            num = num + 1            # pics_urls=re.findall('\'url\': \'.*.jpg\'',card_str)            if not re.search('retweeted_status', card_str) and re.search('\'pics\'', card_str):                for j in range(len(card['pics'])):                    pic_url = card['pics'][j]['large']['url'].replace('\\', '')                    page_info['url'][num] = pic_url                    page_info['id'][num] = card['pics'][j]['pid']                    page_info['createat'][num] = createat                    num = num + 1        except:            None        try:            if i == 0 and card['isTop'] == 1:                top_info['is_top'] = 1                top_info['num_top'] = len(card['pics']) + 1        except:            None    # for i in range(len(page_info['createat'])):    #     page_info['createat'][i]=datetime2mysql(page_info['createat'][i])    return page_info, top_infodef is_num_by_except(str):    try:        int(str)        return True    except:        return Falsedef info2mysql(info):  # 将数据存储入本地的mysql,若出现编码错误，则忽略该条，同名文件会覆盖从前的数据库    sum_insert = 0    user_id = 'user' + info['user_id']    Urls = info['url']    Id = info['id']    Createat = info['createat']    try:        db = pymysql.connect(host, user, password, database, charset='utf8')        # print('CONNECTING SUCESSFULLY')    except:        print('CONNECTING ERROR')    cursor = db.cursor()    try:        cursor.execute("show tables" + ';')        tables = cursor.fetchall()        if tables == {} or (user_id,) not in cursor.fetchall():            sql1 = """CREATE TABLE """            sql2 = """ (                    createat datetime,                    url char(100) NOT NULL,                    id char(50),                    downloaded bool,                    primary key (url)                    )character SET=utf8;"""            sql = sql1 + user_id + sql2            cursor.execute(sql)        else:            None    except:        None    for i in range(len(Urls)):        sql = "insert ignore into " + user_id + """        values("""        createat = datetime2mysql(Createat[i])        sql = sql + createat + ',\"' + Urls[i] + '\",' + '\"' + str(Id[i]) + '\",' + '0' + ');'        try:            cursor.execute(sql)            sum_insert = sum_insert + 1        except:            # print(sql, '\nILLEGAL TEXT')            continue    db.commit()    db.close()    # print('Insert ' + str(sum_insert) + ' pics into ' + info['user_id'])def sinatime2format(sina_time):    ch=sina_time[0:2]    if (sina_time[0:2] == '今天'):        time = (get_time('today')) + sina_time[-6:]    elif (sina_time[0:2] == '昨天'):        time = get_time('yesterday') + sina_time[-6:]    elif (len(sina_time) == 11):        time = (get_time())[0:5] + sina_time    else:        time = sina_time    return timedef datetime2mysql(time):    time = time.replace(':', '')    time = time.replace('-', '')    time = time.replace(' ', '')    if (len(time) != 14):        return time + '00'    else:        return timedef user_add(user_id):    try:        db = pymysql.connect(host, user, password, database, charset='utf8')        cursor = db.cursor()        # print('CONNECTING SUCESSFULLY')    except:        print('CONNECTING ERROR')    try:        sql="insert into weibo_pics.users_info values(\'"+user_id+"\',\'0\',\'None\',\'None\'"        cursor.execute(sql)        db.commit()        db.close()    except:        return Nonedef users_info():    user_info = []    try:        db = pymysql.connect(host, user, password, database, charset='utf8')        cursor = db.cursor()        # print('CONNECTING SUCESSFULLY')    except:        print('CONNECTING ERROR')    try:        sql = "select * from users_info;"        cursor.execute(sql)        users_list = list(cursor.fetchall())        for user_id in users_list:            user_id = (list(user_id))[0]            user_info.append(user_id)    except:        return None    db.commit()    db.close()    return user_infodef check_all_downloaded():    user_list = users_info()    for user_id in user_list:        downloaded2mysql(user_id)def get_all():    user_list = users_info()    # print(list)    # print('Parent process %s.' % os.getpid())    p = Pool(len(user_list) + 1)    for i in range(len(user_list)):        p.apply_async(main, args=(user_list[i],))    print('Waiting for all subprocesses done...')    p.close()    p.join()    print('All subprocesses done.')def onebyone():    sum_done=0    user_list = users_info()    for user_id in user_list:        main(user_id=str(user_id))        sum_done=sum_done+1        print(sum_done,' of ',len(user_list),' done')# print(datetime2mysql('2014-14-14 14:14:14'))# picsinfo2localmysql(user_id='1712539910')# print(sinatime2format('02-20 16:16'))# get_containerid()# error_test()# get_all()# latest_pic_createat('3246862562')# downloaded2mysql('1712539910')# undownloadedpics('1712539910')# main_download('1712539910')# users_info()# check_all_downloaded()# print(info_bottom('1712539910'))# onebyone()