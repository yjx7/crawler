# coding:utf-8
import traceback
import urllib2

import urllib
import re

import pandas as pd
from bs4 import BeautifulSoup
#sys为system的缩写，引入此模块是为了改变默认编码
import sys
global time
reload(sys)
sys.setdefaultencoding('utf8')  #设置系统的编码为utf8，便于输入中文

host = 'http://www.dianping.com'
#自定义UA头部，直接用即可，不用理解细节
# user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.89 Safari/537.36'
user_agent ='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
headers = {'User-Agent':user_agent}
city={'广州':'/4/10','深圳':'/7/10', '韶关':'/205/10','茂名':'/211/10','云浮':'/223/10','梅州':'/214/10','河源':'/216/10','清远':'/218/10','江门':'/209/10','佛山':'/208/10','汕头':'/207/10','潮州':'/221/10','中山':'/220/10','揭阳':'/222/10' ,'湛江':'/210/10','珠海':'/206/10','肇庆':'/212/10','汕尾':'/215/10','阳江':'/217/10','东莞':'/219/10','惠州':'/213/10'}

# key_word = '广州'                                      #写好要搜索的关键词
#                                      #武汉的城市编码为16，其他城市的编码可以在点评网的URL中找到
# directory =  unicode(key_word,'utf8')  #Windows系统下，创建中文目录名前需要制定编码，这里统一用UTF-8

items_name = []
items_address = []
items_caixi = []
items_price = []



def getList(page,citynum):

    page = str(page)
    real_url = host + '/search/category'+city.get(city.keys()[citynum])+'/o2'
    if page!=1:
        real_url = real_url+  'p' + page
    request = urllib2.Request(real_url, headers = headers)                               #发送网络请求
    response = urllib2.urlopen(request)                                                  #得到网络响应
    document = response.read().encode('utf-8')                                          #将网页源码用UTF-8解码
    soup=BeautifulSoup(document,'lxml')
    shop_list=soup.find_all('div',class_='tit')
    return [i.find('a')['href'] for i in shop_list]

def getDocument(page, citynum):

    page = str(page)
    real_url = host + '/search/category'+city.get(city.keys()[citynum])+'/o2'
    if page!=1:
        real_url = real_url+  'p' + page
    request = urllib2.Request(real_url, headers = headers)                               #发送网络请求
    response = urllib2.urlopen(request)                                                  #得到网络响应
    document = response.read().encode('utf-8')                                          #将网页源码用UTF-8解码
    nitems_name = re.findall(r'data-hippo-type="shop"\stitle="([^"]+)"', document, re.S)  #正则匹配出商家名
    nitems_address = re.findall(r'<span\sclass="addr">([^\s]+)</span>', document.strip() , re.S)   #正则匹配出地址
    nitems_caixi= re.findall(r'<span\sclass="tag">([^\s]+)</span>', document, re.S)  # 正则匹配出菜系
    nitems_price = re.findall(r'￥([^\s]+)</b>|class="mean-price" target="_blank">[^\s]+', document.strip().replace("\n", ""), re.S)  # 正则匹配出人均消费|class="mean-price" target="_blank">[^\s]+

    new_items_caixi=[]#得到真正的菜系
    for i in range(len(nitems_caixi)/2):
        new_items_caixi.append(nitems_caixi[2*i])

#正则出去甜点西餐等
    for i in range(len(new_items_caixi)):
        try:
            if re.search(u'面包甜点|咖啡|小吃|日本料理|韩国料理|茶餐厅|粥粉面|自助餐|生日蛋糕|其他|素食|大闸蟹|生鲜水果'.encode('utf8'),new_items_caixi[i]):
                pass
            else:
                items_caixi.append(new_items_caixi[i])
                items_name.append(nitems_name[i])
                items_address.append(nitems_address[i])
                items_price.append(nitems_price[i])
        except:
            traceback.print_exc()
            items_price.append('-')
            print len(items_price), len(items_caixi)
            # for id in range(len(new_items_caixi)):
            #     print new_items_caixi[id],nitems_name[id],nitems_address[id],nitems_price[id]


def start_crawl():
    global time
    for citynum in range(len(city)):
        time=0
        for index in range(1, 100):
            time=len(items_price)
            print time
            getDocument(index,citynum)
            if time>500 and (city.keys()[citynum]==u'深圳' or city.keys()[citynum]==u'广州'):
                break
            elif time>200 and  (city.keys()[citynum]!=u'深圳' or city.keys()[citynum]!=u'广州'):
                break

        ex = []

        for i in range(len(items_price)):
            ex.append([items_name[i], items_caixi[i], items_address[i], items_price[i]])



        df = pd.DataFrame(ex)
        df.to_csv( unicode(city.keys()[citynum],'utf8')+'.csv',encoding='gbk')
        print ('Complete!')
        del items_name[:]
        del items_address[:]
        del items_caixi[:]
        del items_price[:]

start_crawl()  # 开始爬数据！