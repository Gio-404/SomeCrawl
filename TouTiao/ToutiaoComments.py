#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ToutiaoComments.py
@Time    :   2022/11/06 23:29:09
@Author  :   wwb 
@Version :   1.0
@Contact :   weibo0920@gmail.com
'''

import requests
from requests import RequestException
import re
import os
from bs4 import BeautifulSoup
import pymongo
from config import *
from hashlib import md5
from multiprocessing import Pool
import json


client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]


def index_page(page_num):
    '''
    获取主页html代码
    Parameters:
        page_num - 搜索关键词

    Return:
        主页html代码
    '''
    url = 'https://so.toutiao.com/search'
    data = {
        'keyword': KEYWORD,
        'pd': 'weitoutiao',
        'source': 'aladdin_weitoutiao',
        'page_num': page_num,
        'dvpf': 'pc',
        'aid': 4916,
        'from_search_id': '20221108003257010150059016094B4A4A',
    }
    try:
        resp = requests.get(url, params=data, cookies=COOKIE, headers=HEADERS)
        if resp.status_code == 200:
            return resp.text
        return '响应{}错误'.format(resp.status_code)
    except RequestException as e:
        return '请求出错：{}'.format(e)


def parse_index_page(html):
    '''
    解析主页内容
    Parameters:
        html - 主页html代码

    Return:
        (子页面url, group_id)
    '''
    pattern_url = re.compile(r'<a href="(.*?)".*?cs-view cs-view-block d-flex')
    url_list = re.findall(pattern_url, html)
    pattern_id = re.compile(r'/a(.*?)/')
    for u in url_list:
        group_id = re.findall(pattern_id, u.split('?')[0])[0]
        yield u.split('?')[0], group_id


def detail_index(url):
    '''
    获取子页面html代码
    Parameters:
        url - 子页面url

    Return:
        子页面html代码
    '''
    try:
        resp = requests.get(url, cookies=COOKIE, headers=HEADERS)
        if resp.status_code == 200:
            return resp.text
        return '响应{}错误'.format(resp.status_code)
    except RequestException as e:
        return '请求出错：{}'.format(e)


def parse_detail_index(html, url):
    '''
    解析子页面内容
    Parameters:
        html - 子页面html代码
        url - 子页面url

    Return:
        {
            'title': 子页面标题,
            'url': 子页面url,
            'src_list': 图片链接
        }
    '''
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string
    images = soup.find_all(name='img', attrs={'class': 'weitoutiao-img'})
    if images:
        src_list = ['https:' + i['src'] for i in images]
        for src in src_list:
            download_image(src)
        return {'title': title, 'url': url, 'src_list': src_list}


def save_mongo_data(result, table_name):
    '''
    保存数据到mongodb
    Parameters:
        result - 要保存的数据dict格式
        table_name - 数据表名

    Return:
        保存结果
    '''
    if db[table_name].insert_one(result):
        print('存储到mongodb成功', result)
        return True
    return False


def download_image(url):
    '''
    获取图片响应
    Parameters:
        url - 图片url

    Return:
        下载链接响应code
    '''
    print('Downloading:%s' % url)
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            save_image(resp.content)
        return resp.status_code
    except RequestException as e:
        return '请求{}出错：{}'.format(url, e)


def save_image(content):
    '''
    保存图片
    Parameters:
        content - 二进制图片内容
    '''
    path = os.path.split(os.path.realpath(__file__))[0]
    file_path = path + '\images\{}.jpg'.format(md5(content).hexdigest())
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)


def parse_reply_data(group_id):
    '''
    获取评论数据
    Parameters:
        group_id - 子页面group_id

    Return:
        {
            'group_id' : 子页面group_id,
            'username' : 用户名,
            'located' : 地点,
            'text' : 评论内容
        }
    '''
    url = 'https://www.toutiao.com/article/v2/tab_comments/'
    data = {
        'aid': 24,
        'app_name': 'toutiao_web',
        'offset': 0,
        'count': 20,
        'group_id': group_id,
        'item_id': group_id,
    }
    try:
        resp = requests.get(url, params=data, cookies=COOKIE, headers=HEADERS)
        if resp.status_code == 200 and len(resp.json()['data']) > 0:
            data = resp.json()['data']
            for rp in data:
                reply_info = {
                    'group_id': group_id,
                    'username': rp['comment']['user_name'],
                    'located': rp['comment']['publish_loc_info'],
                    'text': rp['comment']['text'],
                }
                yield reply_info
    except RequestException as e:
        return '请求出错：{}'.format(e)


def main(offset):
    pid = os.getpid()
    try:
        index_html = index_page(offset)
        for u in parse_index_page(index_html):
            detail_html = detail_index(u[0])
            if detail_html:
                result = parse_detail_index(detail_html, u[0])
                save_mongo_data(result, 'toutiao')
                for rp in parse_reply_data(u[1]):
                    save_mongo_data(rp, 'reply')
    except KeyboardInterrupt:
        print('进程%d被强制中断...' % pid)


if __name__ == '__main__':
    # main()
    try:
        groups = [p for p in range(GROUP_START, GROUP_END + 1)]
        pool = Pool()
        pool.map(main, groups)
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        pid = os.getpid()
        os.popen('taskkill.exe /f /pid:%d' % pid)
    except Exception as e:
        print(e)
