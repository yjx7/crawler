# coding:utf-8
import traceback
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import getIp
#sys为system的缩写，引入此模块是为了改变默认编码
import sys
global time
reload(sys)
import io
sys.setdefaultencoding('utf8')  #设置系统的编码为utf8，便于输入中文
host = 'http://www.dianping.com'
user_agent ='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'#'揭阳':'/222/10' ,'韶关':'/205/10','茂名':'/211/10','云浮':'/223/10','梅州':'/214/10','汕头':'/207/10','肇庆':'/212/10',,'湛江':'/210/10','河源':'/216/10','佛山':'/208/10','潮州':'/221/10','汕尾':'/215/10','阳江':'/217/10','惠州':'/213/10'
headers = {'User-Agent':user_agent}
city={'广州':'/4/10','深圳':'/7/10'}# ,'珠海':'/206/10','中山':'/220/10','清远':'/218/10','江门':'/209/10'
def get_ip_list():
   return getIp.p_isactive.is_active_proxy_ip
def get_random_ip(ip_list):
    proxies = random.choice(ip_list)
    return proxies
ip_list=get_ip_list()

def re_connection(real_url):
    request=None
    while 1:
        try:
            proxies = get_random_ip(ip_list)
            request = requests.get(real_url, headers=headers, proxies=proxies)  # 发送网络请求,
            break
        except:
            traceback.print_exc()
            print("ZZzzzz...")
            print(" continue...")
            continue
    return request

items_name = []
items_address = []
items_caixi = []
items_price = []
items_point=[]
def getDocument(page, citynum):
    page = str(page)
    real_url = host + '/search/category'+city.get(city.keys()[citynum])+'/o2'
    if page!=1:
        real_url = real_url+  'p' + page
    request=re_connection(real_url)
    document=BeautifulSoup(request.text,'lxml')

    nitems_names = document.find_all('div',class_='tit')
    nitems_addresses = document.find_all('span',class_='addr')
    nitems_caixis= document.find_all('span',class_='tag')
    nitems_prices = document.find_all('a',class_='mean-price')
    nitems_pointss=document.find_all('span',class_='comment-list')

    txt=document.find_all('div',class_='txt')
    flag=[]
    for i,t in enumerate(txt):
        if t.find('span',class_='comment-list') is None:
            flag.append(i)
    if len(flag)!=0:
        print 'point need add 0'
    nitems_point=[]
    nitems_name=[]
    nitems_address=[]
    nitems_price=[]
    new_items_caixi = []  # 得到真正的菜系

    j=0#防止空分数
    for i in range(len(nitems_prices)):
        nitems_name.append(nitems_names[i].find('a')['title'])
        nitems_address.append(nitems_addresses[i].text)
        nitems_price.append(nitems_prices[i].text)
        point_team=[]
        if i in flag:
            j+=1
            nitems_point.append(['0','0','0'])
            continue
        points=nitems_pointss[i-j].find_all('b')
        for point in points:
            point_team.append(point.text)
        nitems_point.append(point_team)

    for i in range(len(nitems_caixis)/2):
        new_items_caixi.append(nitems_caixis[2*i].text)
#正则出去甜点西餐等
    for i in range(len(new_items_caixi)):
        try:
            if re.search(u'面包甜点|咖啡|小吃|日本料理|韩国料理|茶餐厅|粥粉面|自助餐|生日蛋糕|其他|素食|大闸蟹|生鲜水果'.encode('utf8'),new_items_caixi[i].encode('utf8')):
                print 're pass food'
            else:
                items_caixi.append(new_items_caixi[i])
                items_name.append(nitems_name[i])
                items_address.append(nitems_address[i])
                items_price.append(nitems_price[i])
                items_point.append(nitems_point[i])
        except:
            traceback.print_exc()
def start_crawl():
    global time
    for citynum in range(len(city)):
        time=0
        for index in range(1, 100):
            time=len(items_price)
            print time
            getDocument(index,citynum)
            if time>500:
                break
        ex = []
        for i in range(len(items_price)):
            price = re.search("[0-9]+", items_price[i]).group() if re.search("[0-9]+", items_price[i])!=None else '-'
            ex.append([items_name[i].strip(), items_caixi[i].strip(), items_address[i].strip(), price,items_point[i][0].strip(),items_point[i][1].strip(),items_point[i][2].strip(),float(items_point[i][0])+float(items_point[i][1])+float(items_point[i][2])])#kw hj fw

        df = pd.DataFrame(ex,columns =[u"店名",u"菜系",u"地址",u"人均",
                                                                                     u"口味",u"环境",u"服务",u"总分"])
        try:
            df.to_csv( unicode(city.keys()[citynum],'utf8')+'.csv',encoding='GB18030')#encoding='gbk'
        except:
            print unicode(city.keys()[citynum],'utf8')
            traceback.print_exc()
            try:
                df.to_csv(str(random.randint(1,100) )+ '.csv', encoding='GB18030')
            except:
                traceback.print_exc()
                print '....wow'

        print ('Complete!')
        del items_name[:]
        del items_address[:]
        del items_caixi[:]
        del items_price[:]
        del items_point[:]
start_crawl()  # 开始爬数据！