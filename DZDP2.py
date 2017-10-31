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
user_agent ="'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'"

headers = {'User-Agent':user_agent}
city={'广州':'/4/10','深圳':'/7/10', '韶关':'/205/10','茂名':'/211/10','云浮':'/223/10','梅州':'/214/10','河源':'/216/10','清远':'/218/10','江门':'/209/10','佛山':'/208/10','汕头':'/207/10','潮州':'/221/10','中山':'/220/10','揭阳':'/222/10' ,'湛江':'/210/10','珠海':'/206/10','肇庆':'/212/10','汕尾':'/215/10','阳江':'/217/10','东莞':'/219/10','惠州':'/213/10'}
ip=[{"ip":"223.247.156.24","port":3852},{"ip":"111.78.190.239","port":9756},{"ip":"58.243.205.173","port":9858},{"ip":"123.156.181.21","port":2156},{"ip":"123.156.178.239","port":2156},{"ip":"115.209.49.123","port":5439},{"ip":"182.100.66.132","port":7685},{"ip":"106.57.6.111","port":3429},{"ip":"49.88.213.128","port":5638},{"ip":"49.88.104.207","port":5638},{"ip":"111.72.100.16","port":9756},{"ip":"180.109.35.105","port":4813},{"ip":"115.237.82.94","port":2315},{"ip":"27.220.226.219","port":8878},{"ip":"117.69.51.148","port":2319},{"ip":"223.245.87.140","port":4534},{"ip":"222.190.204.75","port":3798},{"ip":"117.94.69.58","port":3798},{"ip":"1.86.88.67","port":2319},{"ip":"117.33.23.68","port":2319},{"ip":"223.245.102.219","port":4534},{"ip":"119.180.201.77","port":7856},{"ip":"180.118.93.95","port":3217},{"ip":"114.101.52.160","port":4534},{"ip":"182.240.7.60","port":3245}]
items_name = []
items_address = []
items_caixi = []
items_price = []
items_kwp= []
items_hjp = []
items_fwp = []
def get_ip_list():
    ip_list = []
    for i in range(len(ip)):
        ip_list.append(str(ip[i]['ip'])+':'+str(ip[i]['port']))
    return ip_list
# def get_ip_list(url, headers):
#     web_data = requests.get(url+str(random.randint(1,2488)), headers=headers)
#     soup = BeautifulSoup(web_data.text, 'lxml')
#     ips = soup.find_all('tr')
#     ip_list = []
#     for i in range(1, len(ips)):
#         ip_info = ips[i]
#         tds = ip_info.find_all('td')
#         ip_list.append(tds[1].text + ':' + tds[2].text)
#     return ip_list

def get_random_ip(ip_list):
    proxy_list = []
    for ip in ip_list:
        proxy_list.append('http://' + ip)
    proxy_ip = random.choice(proxy_list)
    proxies = {'http': proxy_ip}
    return proxies


ipurl = 'http://www.xicidaili.com/nn/'
# ipurl='http://www.kuaidaili.com/free/inha/2/'


def getList(page,citynum,ip_list):
    page = str(page)
    real_url = host + '/search/category'+city.get(city.keys()[citynum])+'/o2'
    if page!=1:
        real_url = real_url+  'p' + page
    # request = requests.get(real_url, headers = headers, proxies=proxies)
    while 1:
        try:
            proxies = get_random_ip(ip_list)
            print(proxies)
            request = requests.get(real_url, headers=headers, proxies=proxies)  # 发送网络请求
            break
        except:
            print("ZZzzzz...")
            time.sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue
    #发送网络请求
    soup=BeautifulSoup(request.text,'lxml')
    shop_list=soup.find_all('div',class_='tit')
    return [i.find('a')['href'] for i in shop_list]

def getDocument(page, citynum,ip_list):
    list=getList(page,citynum,ip_list)
    print 123
    for i in range(len(list)):
        while 1:
            try:
                proxies = get_random_ip(ip_list)
                print(proxies)
                request =requests.get(list[i], headers=headers)  # 发送网络请求, proxies=proxies
                soup = BeautifulSoup(request.text, 'lxml')
                point = soup.find('span', id='comment_score').find_all('span', class_='item')  # 评分
                name = soup.find('div', class_='breadcrumb').find('span').text
                address = soup.find('span', itemprop='street-address').text
                caixi = soup.find('div', class_="breadcrumb").find_all('a')[1].text.strip()
                price = soup.find('span', id='avgPriceTitle').text
                break
            except:
                print("ZZzzzz...")
                time.sleep(5)
                print("continue...scrapy")
                continue



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
    ip_list = get_ip_list()
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