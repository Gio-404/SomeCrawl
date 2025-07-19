#!usr/bin/env python3
# coding:utf-8

# @Author: WWB
# @CurrentFile: spiderlg.py
# @DateTime: 2019/5/3 18:56


import requests
from bs4 import BeautifulSoup
import re
import os
import json
import logging

path = os.getcwd()
with open(path + "\headers.txt", encoding="UTF-8") as f:
    headers = json.loads(f.read())
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d, %b %Y %H:%M:%S')


class SpiderLg():
    def __init__(self):
        self.base_url = "https://www.lagou.com/"
        self.headers = headers

    def get_works(self):
        i = 0
        while i < 3:
            try:
                resp_lg = requests.get(
                    self.base_url, headers=self.headers, timeout=5)
                logging.debug("Request: %s Status: %s" %
                              (self.base_url, resp_lg.status_code))
                resp_content = resp_lg.content
                if resp_lg.status_code == 200:
                    work = BeautifulSoup(resp_content, "html.parser")
                    pattern = re.compile(r".*ceshi.*")
                    href_list = []
                    for link in work.findAll("a"):
                        get_href = str(link.get("href"))
                        if re.findall(pattern, get_href):
                            href_list.append(get_href)
                    return href_list
                else:
                    raise Exception("RequestError:" + resp_lg.status_code)
            except requests.exceptions.RequestException as e:
                logging.debug(e)
                i += 1
            break

    def query_works(self):
        i = 0
        position = SpiderLg.get_works(self)
        if len(position) != 0:
            for link in position:
                while i < 3:
                    try:
                        resp_content = requests.post(
                            link, headers=headers, timeout=5)
                        logging.debug("Request: %s Status: %s" %
                                      (link, resp_content.status_code))
                        resp_position = resp_content.content
                        if resp_content.status_code == 200:
                            content = BeautifulSoup(
                                resp_position, "html.parser")
                            position_info = content.find_all(
                                "li", class_="con_list_item default_list")
                            pattern_exp = re.compile(r"(?<=<!--<i></i>-->).+")
                            pattern_add = re.compile(r"(?<=<em>).+(?=</em>)")
                            for li in position_info:
                                company = li["data-company"]
                                positionname = li["data-positionname"]
                                salary = li["data-salary"]
                                address = re.findall(pattern_add, str(li))[0]
                                exp = re.findall(pattern_exp, str(li))[0]
                                return company, positionname, salary, address, exp

                        else:
                            raise Exception("RequestError:" +
                                            resp_content.status_code)
                    except requests.exceptions.RequestException as e:
                        logging.debug(e)
                        i += 1
                    break
        else:
            logging.debug("List is null!")

if __name__ == '__main__':
    sp = SpiderLg()
    sp.get_works()
    print(sp.query_works())