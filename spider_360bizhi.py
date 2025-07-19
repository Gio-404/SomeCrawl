#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   spider_360bizhi.py
@Time    :   2021/10/23 16:44:48
@Author  :   wwb
@Version :   1.0
@Contact :   weibo0920@gmail.com
"""

# here put the import lib
import requests
import random
import time
import os
import sys
import threading
import re

header = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                    "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                        "Chrome/95.0.4638.54 Safari/537.36"
          }
# [5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 18, 22, 26, 29, 30, 35, 36]
cid_list = [13, 15, 16, 18, 22, 26, 29, 30, 35, 36]
category_url = "http://wp.shanhutech.cn/intf/GetListByCategory"
count = 20


def get_category(cid, pageno=0, page_count=10):
    time.sleep(1)
    category_resp = requests.get(category_url + "?cids={}&pageno={}&count={}".format(cid, pageno, page_count), headers=header, timeout=30)
    result = category_resp.json()
    return result


def create_dir(name):
    category_path = os.path.abspath(name)
    if not os.path.exists(name):
        os.makedirs(name)
        sys.stdout.write(name + '-目录创建成功' + '\n')
    else:
        pass
        sys.stdout.write(name + '-目录已存在' + '\n')
    return category_path


def get_url_list(cid):
    page_no = 1
    url_list = []
    result_data = get_category(cid)['data']
    # total_page = result_data['total_page']
    total_page = 6
    category_name = result_data['list'][0]['category']
    file_path = create_dir(category_name)
    sys.stdout.write("正在获取-%s-图片地址......" % category_name + "\n")
    while page_no < total_page:
        next_page = get_category(cid, page_no, count)
        image_list = next_page['data']['list']
        for u1 in image_list:
            url_list.append(u1['url'])
        page_no += 1
    sys.stdout.write("%s获取完成" % category_name + "\n")
    return file_path, url_list


def url_list_suite(cid_list_param):
    for c in cid_list_param:
        cid_tuple = get_url_list(c)
        yield cid_tuple


def random_name(name):
    image_name = name
    if image_name is None:
        image_name = ''.join(str(random.choice(range(10))) for _ in range(10)) + '.jpg'
    else:
        image_name = image_name.group()
    return image_name


def download_image(file_path, url_list):
    for u2 in url_list:
        image_name = re.search(r'(?<=--).*.jpg', u2)
        image_name = random_name(image_name)
        image_path = file_path + '\\{}'.format(image_name)
        sys.stdout.write("开始下载%s" % u2 + "\n")
        time.sleep(1)
        image_resp = requests.get(u2, stream=True, headers=header, timeout=30)
        with open(image_path, 'wb') as f:
            for chunk in image_resp.iter_content():
                f.write(chunk)
            sys.stdout.write("%s下载成功" % u2 + "\n")


lock = threading.Lock()


def loop(suites):
    while True:
        try:
            with lock:
                cate_list = next(suites)
        except StopIteration:
            break
        print(cate_list[0], cate_list[1])
        download_image(cate_list[0], cate_list[1])


suites = url_list_suite(cid_list)
for i in range(0, 3):
    t = threading.Thread(target=loop, name='LoopThread %s' % i, args=(suites,))
    t.start()
