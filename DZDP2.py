# coding:utf-8
import traceback
import urllib2

import urllib
import re

import pandas as pd
from bs4 import BeautifulSoup
import sys
import time
global times
import requests
import random
reload(sys)
sys.setdefaultencoding('utf8')  #设置系统的编码为utf8，便于输入中文

host = 'http://www.dianping.com'

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
           }
city={'广州':'/4/10','深圳':'/7/10', '韶关':'/205/10','茂名':'/211/10','云浮':'/223/10','梅州':'/214/10','河源':'/216/10','清远':'/218/10','江门':'/209/10','佛山':'/208/10','汕头':'/207/10','潮州':'/221/10','中山':'/220/10','揭阳':'/222/10' ,'湛江':'/210/10','珠海':'/206/10','肇庆':'/212/10','汕尾':'/215/10','阳江':'/217/10','东莞':'/219/10','惠州':'/213/10'}
items_name = []
items_address = []
items_caixi = []
items_price = []
items_kwp= []
items_hjp = []
items_fwp = []
def get_ip_list():
   return Getip.p_isactive.is_active_proxy_ip
def get_random_ip(ip_list):
    proxies = random.choice(ip_list)
    return proxies
ip_list=get_ip_list()

def get_connection(real_url):
    request=None
    while 1:
        try:
            proxies = get_random_ip(ip_list)
            request = requests.get(real_url, headers=headers, proxies=proxies)  # 发送网络请求,
            break
        except:
            traceback.print_exc()
            print("re continue...")
            continue
    return request

def getList(page,citynum,ip_list):
    page = str(page)
    real_url = host + '/search/category'+city.get(city.keys()[citynum])+'/o2'
    if page!=1:
        real_url = real_url+  'p' + page
    request=get_connection(real_url)
    #发送网络请求
    soup=BeautifulSoup(request.text,'lxml')
    shop_list=soup.find_all('div',class_='tit')
    return [i.find('a')['href'] for i in shop_list]

def getDocument(page, citynum,ip_list):
    list=getList(page,citynum,ip_list)
    print 123
    for i in range(len(list)):
        request = get_connection(real_url)
        soup = BeautifulSoup(request.text, 'lxml')
        point = soup.find('span', id='comment_score').find_all('span', class_='item')  # 评分
        name = soup.find('div', class_='breadcrumb').find('span').text
        address = soup.find('span', itemprop='street-address').text
        caixi = soup.find('div', class_="breadcrumb").find_all('a')[1].text.strip()
        price = soup.find('span', id='avgPriceTitle').text
    #正则出去甜点西餐等
        try:
            if re.search(u'面包甜点|咖啡|小吃|日本料理|韩国料理|茶餐厅|粥粉面|自助餐|生日蛋糕|其他|素食|大闸蟹|生鲜水果'.encode('utf8'),caixi):
                pass
            else:
                items_caixi.append(caixi)
                items_name.append(name)
                items_address.append(address)
                items_price.append(price)
                items_kwp.append(point[0].text)
                items_hjp.append(point[1].text)
                items_fwp.append(point[2].text)
        except:
            traceback.print_exc()
            items_price.append('-')
            print len(items_price), len(items_caixi)
        print '-'

def start_crawl():
    global times
    for citynum in range(len(city)):
        times=0
        # ip_list = get_ip_list(ipurl, headers=headers)

        for index in range(1, 100):
            times=len(items_price)
            print times
            getDocument(index,citynum,ip_list)
            if times>500 and (city.keys()[citynum]==u'深圳' or city.keys()[citynum]==u'广州'):
                break
            elif times>200 and  (city.keys()[citynum]!=u'深圳' or city.keys()[citynum]!=u'广州'):
                break

        ex = []

        for i in range(len(items_price)):
            ex.append([items_name[i], items_caixi[i], items_address[i], items_price[i],items_kwp[i],items_hjp[i],items_fwp[i],int(items_kwp[i])+int(items_hjp[i])+int(items_fwp[i])])
        df = pd.DataFrame(ex)
        df.to_csv( unicode(city.keys()[citynum],'utf8')+'.csv',encoding='gbk',names=[u"店名",u"菜系",u"地址",u"人均",u"口味",u"环境",u"服务",u"总分"])
        print ('Complete!')
        del items_name[:]
        del items_address[:]
        del items_caixi[:]
        del items_price[:]
        del items_kwp[:]
        del items_hjp[:]
        del items_fwp[:]

start_crawl()  # 开始爬数据！