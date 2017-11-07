# coding:utf-8

from gevent import monkey
monkey.patch_all()

import urllib2
from gevent.pool import Pool

import random
import requests
from bs4 import BeautifulSoup


class SpiderProxy(object):
    """
    从http://www.xicidaili.com/wt 取代理ip
    """
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
    headers = {
        "Host": "www.xicidaili.com",
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "http://www.xicidaili.com/wt/1",
    }

    def __init__(self, session_url):
        self.req = requests.session()
        self.req.get(session_url)



    def get_pagesource(self, url):
        '''取得html pagesource'''
        list = open('ip.txt', 'r').read()
        proxies = random.choice(list)
        html = self.req.get(url, headers=self.headers,proxies=proxies)
        return html.content

    def get_all_proxy(self, url, n):
        ''' 取得所有1-n页上的代理IP'''
        data = []
        for i in range(n-10, n):
            html = self.get_pagesource(url + str(i))
            soup = BeautifulSoup(html, "lxml")

            table = soup.find('table', id="ip_list")
            for row in table.findAll("tr"):
                cells = row.findAll("td")
                tmp = []
                for item in cells:

                    tmp.append(item.find(text=True))
                try:
                    tmp2 = tmp[1:2][0]
                    tmp3 = tmp[2:3][0]
                    tmp4 = tmp[5:6][0]
                    data.append({tmp4: tmp2 + ":" + tmp3})
                except Exception as e:
                    pass
        return data


class IsActivePorxyIP(object):
    """类组合
     用gevent 异步并发验证 代理IP是不是可以用
    """

    def __init__(self, session_url):
        self.proxy = SpiderProxy(session_url)
        self.is_active_proxy_ip = []

    def probe_proxy_ip(self, proxy_ip):
        """代理检测"""
        proxy = urllib2.ProxyHandler(proxy_ip)
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)
        try:
            html = urllib2.urlopen('http://1212.ip138.com/ic.asp')
            # html=urllib2.urlopen('http://hz.meituan.com/meishi/')
            # print html.read()
            if html:#re.search('403 Forbidden',html)==None:#html
                self.is_active_proxy_ip.append(proxy_ip)
                return True
            else:
                return False
        except Exception as e:
            return False


if __name__ == '__main__':

    session_url = 'http://www.xicidaili.com/wt/1'
    url = 'http://www.xicidaili.com/wt/'

    p_isactive = IsActivePorxyIP(session_url)
    proxy_ip_lst = p_isactive.proxy.get_all_proxy(url, random.randint(11,100))

    # 异步并发
    pool = Pool(20)
    pool.map(p_isactive.probe_proxy_ip, proxy_ip_lst)
    print p_isactive.is_active_proxy_ip
