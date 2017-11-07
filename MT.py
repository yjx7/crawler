# coding:utf-8
import traceback
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
# import getIp
import time
#sys为system的缩写，引入此模块是为了改变默认编码
import sys
global times
reload(sys)
sys.setdefaultencoding('utf8')  #设置系统的编码为utf8，便于输入中文
user_agents = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
]
headers = {'User-Agent':random.choice(user_agents)}

city = { '湛江':'zhanjian'}#  '阳江': 'yj','中山': 'zs','江门': 'jm', '清远': 'qingyuan','汕尾': 'sw','广州': 'gz', '深圳': 'sz',,'肇庆':'zq', '茂名': 'mm', '潮州': 'chaozhou', '珠海': 'zh', '河源': 'heyuan', '佛山': 'fs'
def get_ip_list():
   # return Getip.p_isactive.is_active_proxy_ip  #直接获取IP池
    list = open('ip.txt', 'r').read()#从文件中读取
    return list
def get_random_ip(ip_list):
    proxies = random.choice(ip_list)
    return proxies

ip_list=get_ip_list()
global proxies
proxies = get_random_ip(ip_list)#从IP池中随机选取一个IP

#重新获取IP，并请求
def re_connection(real_url,base_url):#
    global proxies
    request=None
    while 1:
        try:
            host=base_url
            #time.sleep(1)
            headers={'Host':host,'Connection': 'keep-alive','Origin': 'http://'+base_url,'User-Agent':random.choice(user_agents),'Accept': '*/*','Referer':real_url,'Accept-Encoding': 'gzip, deflate','Accept-Language': 'zh-CN,zh;q=0.8'}
            request = requests.get(real_url, headers=headers, proxies=proxies)  # 发送网络请求,
            if re.search('403 Forbidden',request.text):
                proxies = get_random_ip(ip_list)#403被限制访问，从IP池中重新随机选取一个IP
                continue
            break
        except:
            traceback.print_exc()
            print("ZZzzzz...")
            proxies = get_random_ip(ip_list)#其他错误，从IP池中重新随机选取一个IP
            print(" continue...")
            continue
    return request

items_name = []#商家名称，下同
items_address = []
items_caixi = []
items_price = []
items_point=[]
ex=[]#装每一页中，以上的内容


#得到网站的内容
def getDocument(page, citynum):

    page = str(page)
    base_url=city.get(city.keys()[citynum])+'.meituan.com'
    real_url ='http://'+base_url+'/meishi/renqi/pn'+page #获取根据人气排行的美食
    # real_url = 'http://' + base_url + '/meishi/c20816/pn' + page  #这个是获取粤菜的
    request = re_connection(real_url,base_url)
    document = BeautifulSoup(request.text, 'lxml')
     # 标题信息
    items_info=document.find_all('a',class_='item-title')#标题
    for i in items_info:
        items_name.append(i.text)

    #地址和菜品信息
    items_info=document.find_all('div', class_='item-site-info clearfix')
    for i in items_info:
        span=i.find_all('span')
        caixi=re.findall(r"(.*)\|(.*)", span[0].text)[0][0] #匹配  中餐|天河区  匹配 中餐
        items_caixi.append(caixi)
        items_address.append(span[1].text)


    txt=document.find_all('div',class_='list-item-desc-top')
    flag=[]
    for i,t in enumerate(txt):
        if t.find('div', class_='item-price-info') is None:
            flag.append(i)
    if len(flag)!=0:
        print 'point need add -'
        # 价格信息
    items_info = document.find_all('div', class_='item-price-info')
    j=0
    for i in range(len(items_info)):
        if i in flag:
            j += 1
            items_price.append('-')
            continue
        price = re.search("[0-9]+", items_info[i-j].find('span').text).group()
        items_price.append(price)

        if i+1==len(items_info):
            for z in range(j):
                price = re.search("[0-9]+", items_info[i - j+z+1].find('span').text).group()
                items_price.append(price)
            break

     # 评分信息
    items_info=document.find_all('div', class_='item-eval-info clearfix')
    for i in items_info:
        span=i.find_all('span')
        items_point.append(span[0].text)

    #因特殊需求，需要除去甜点西餐等
    # 使用正则除去
    for i in range(len(items_caixi)):
        try:
            if re.search(u'.*面包|.*甜点.*|冰淇淋|糕点店|咖啡|小吃|.*料理|茶餐厅|.*粥.*|.*粉.*|.*面.*|过桥米线|.*自助.*|.*蛋糕|其他|素食|大闸蟹|.*生鲜|.*水果|快餐|.*甜.*|.*果.*|日.*|韩.*|.*西.*|.*寿司.*|.*吧|披萨|.*串|牛杂|.*豆.*|饮.*|麻辣烫|汉堡|三明治|.*包.*|意.*|鸡架|.*线|.*饺.*|炖.*|快餐|.*甜.*|.*果.*|日.*|韩.*|.*西.*|.*寿司.*|.*吧|披萨|.*串|牛杂|.*豆.*|饮.*|麻辣烫|汉堡|三明治|.*包.*|意.*|鸡架|.*线|.*饺.*|炖.*'.encode('utf8'),
                         items_caixi[i].encode('utf8')):
                print 're pass food'
            else:
                    ex.append([items_name[i].strip(), items_caixi[i].strip(), items_address[i].strip(),  items_price[i].strip(),
                               items_point[i].strip()])

        except:
            traceback.print_exc()

    #每一页就清空商家各属性的list
    del items_name[:]
    del items_address[:]
    del items_caixi[:]
    del items_price[:]
    del items_point[:]

#爬取数据
def start_crawl():
    global times
    for citynum in range(len(city)):
        times=0#记录商家数
        for index in range(1, 33):#循环爬取1-32页的内容
            times=len(ex)
            print times
            if times>100:#符合的商家大于100就结束
                break
            getDocument(index,citynum)
        df = pd.DataFrame(ex,columns =[u"店名",u"菜系",u"地址",u"人均",u"总分"])
        df.to_csv(unicode(city.keys()[citynum], 'utf8') + '.csv', encoding='GB18030')
        print ('Complete!')
        del ex[:]

start_crawl()  # 开始爬数据！