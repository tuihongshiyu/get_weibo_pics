import os
list_path = '/Users/HirosueRyouko/Pictures/From Weibo/ID_LIST.txt'
def list_initialize():
    if not os.path.exists(list_path):
        f=open(list_path,'w')
        f.close()
        print('-------New List Created')
    else:
        os.remove(list_path)
        print('-------List Deleted')
        f = open(list_path, 'w')
        f.close()
        print('-------New List Created')
    print('-------List Initialization Done')

def list_append(id):
    if type(id)!=int:
        print('-------Illegal Input')
        return
    else:
        id=str(id)

    if not os.path.exists(list_path):
        f=open(list_path,'w')
        f.close()
        print('-------New List Created')
    else:
        f_r = open(list_path, 'r')
        list=f_r.readlines()
        if id+'\n' in list:
            print('-------Existed:'+id)
            return
        else:
            f_w = open(list_path, 'a')
            f_w.write(id + '\n')
            f_w.close()
            list_show()

def list_delete(id):
    if type(id)!=int:
        print('-------Illegal Input')
        return
    else:
        id=str(id)
        # print(id)

    if not os.path.exists(list_path):
        f=open(list_path,'w')
        f.close()
        print('-------There Is No List Existed\n','-------New List Created')
    else:
        f_r = open(list_path, 'r')
        list=f_r.readlines()
        f_r.close()
        if id+'\n' in list:
            print('-------Existed:'+id)
            f_w = open(list_path, 'w')
            f_w.write('')
            f_w.close()

            f_a=open(list_path,'a')
            list.remove(id+'\n')
            for list_id in list:
                f_a.write(list_id)
            f_a.close()
            list_show()
        else:
            print('--------Not Existed:'+id)
            list_show()



def list_show():
    if not os.path.exists(list_path):
        f = open(list_path, 'r')
        f.close()
        print('-------New List Created')
    else:
        print('-------Id List Following')
        f_r = open(list_path, 'r')
        list=f_r.readlines()
        # print(list)
        for id in list:
            id=id[:-1]
            print(id)
        f_r.close()
def list_get():
    if not os.path.exists(list_path):
        print('No exist')
        return None
    else:
        f_r = open(list_path, 'r')
        list=f_r.readlines()
        # print(list)
        for i  in range(len(list)):
            list[i]=list[i][:-1]
        f_r.close()
        return list
# list_initialize()
# list_append()
# list_delete()
# list_show()
# list_get()