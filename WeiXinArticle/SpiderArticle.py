#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   SpiderArticle.py
@Time    :   2022/12/17 15:17:37
@Author  :   wwb 
@Version :   1.0
@Contact :   weibo0920@gmail.com
'''

# here put the import lib
import requests
from requests.exceptions import ConnectionError
from config import *
from pyquery import PyQuery as pq
import re
import random
from bs4 import BeautifulSoup


base_url = 'https://weixin.sogou.com'
cookies = COOKIES
# proxy_pool_url = 'http://192.168.31.15:5555/random'
# proxy = None
# max_count = 5


# def get_proxy():
#     try:
#         resp = requests.get(proxy_pool_url)
#         if resp.status_code == 200:
#             return resp.text
#         return None
#     except ConnectionError as e:
#         print('Error Occurred:', e.args)


def update_snuid():
    other_url = 'https://www.sogou.com/web?query=test'   
    try:
        resp_snuid = requests.get(other_url, headers=HEADERS)
        if resp_snuid.status_code == 200:
            pattern = re.compile(r'token=(.*?)\';')
            token = re.findall(pattern, resp_snuid.text)
            cookies['SNUID'] = token[0][8:40]
            return cookies
        return None
    except ConnectionError as e:
        print('Error Occurred:', e.args)


def wrong_page(html):
    parse_html = pq(html)
    info = parse_html('p.ip-time-p').text()
    return info


def get_html(data):
    global cookies
    try:
        resp = requests.get(base_url + '/weixin', params=data, headers=HEADERS, cookies=cookies)
        if resp.status_code != 200 or wrong_page(resp.text):
            cookies = update_snuid()
            print("更新snuid：%s" % cookies['SNUID'])
            return get_html(data)
        return resp.text
    except ConnectionError as e:
        print('Error Occurred:', e.args)
        


def get_url(resp):
    html = BeautifulSoup(resp, 'lxml')
    article_list = html.find_all(name='a', uigs=re.compile('article_image_\d'))
    for u in list(set(article_list)):
        article_url = base_url + u['href']
        print('解析前的url：', article_url)
        try:
            article_resp = requests.get(article_url, headers=HEADERS, cookies=cookies)
            if article_resp.status_code == 200:
                pattern = re.compile(r"url \+= '(.*)';")
                url_list = re.findall(pattern, article_resp.text)
                wx_url = ''.join(url_list)
                print('解析后的url：', wx_url)
            else:
                print('Response Error:%s'%article_resp.request)
        except ConnectionError as e:
            print('Error Occurred:', e.args)
        


def weixin_url(source_url):
    try:
        article_resp = requests.get(source_url, headers=HEADERS, cookies=cookies)
        if article_resp.status_code == 200:
            pattern = re.compile(r"url \+= '(.*)';")
            url_list = re.findall(pattern, article_resp.text)
            wx_url = ''.join(url_list)
            print(wx_url)
        else:
            print('Response Error:%s'%article_resp.request)
    except ConnectionError as e:
        print('Error Occurred:', e.args)
    

def get_article(wx_url):
    pass


def get_index(keyword, page):
    data = {
        'query': keyword,
        'type': 2,
        'page': page
    }
    return get_html(data)


def main():
    for i in range(2,3):
        html = get_index('风景', i)
        get_url(html)


if __name__ == '__main__':
    main()