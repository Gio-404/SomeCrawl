#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   SpiderMaoyanTop100.py
@Time    :   2022/10/23 15:33:12
@Author  :   wwb 
@Version :   1.0
@Contact :   weibo0920@gmail.com
'''

import requests
import re
import json
from requests.exceptions import RequestException
from multiprocessing import Pool


cookies = {
    '__mta': '188530199.1666509954126.1667635354224.1667635359453.27',
    'uuid_n_v': 'v1',
    'uuid': 'ED3FED5052A311EDAB1EB1434CB45C697184337C285F4E37A6E500A618D5FA57',
    '_lxsdk_cuid': '18403bbda83c8-04cca6df4361e7-26021f51-1fa400-18403bbda83c8',
    '_lxsdk': 'ED3FED5052A311EDAB1EB1434CB45C697184337C285F4E37A6E500A618D5FA57',
    '_lx_utm': 'utm_source%3Dbing%26utm_medium%3Dorganic',
    '__mta': '188530199.1666509954126.1667115013638.1667397229833.19',
    '_csrf': 'a1f971fd7cf26d6f88a68dcdd426abc93ff4bc88c295546c89b7664b4d755e4d',
    'Hm_lvt_703e94591e87be68cc8da0da7cbd0be2': '1667031457,1667110630,1667397227,1667635316',
    'Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2': '1667635359',
    '_lxsdk_s': '18446ed730a-1f4-b1-22f%7C%7C1',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    # Requests sorts cookies= alphabetically
    # 'Cookie': '__mta=188530199.1666509954126.1667635354224.1667635359453.27; uuid_n_v=v1; uuid=ED3FED5052A311EDAB1EB1434CB45C697184337C285F4E37A6E500A618D5FA57; _lxsdk_cuid=18403bbda83c8-04cca6df4361e7-26021f51-1fa400-18403bbda83c8; _lxsdk=ED3FED5052A311EDAB1EB1434CB45C697184337C285F4E37A6E500A618D5FA57; _lx_utm=utm_source%3Dbing%26utm_medium%3Dorganic; __mta=188530199.1666509954126.1667115013638.1667397229833.19; _csrf=a1f971fd7cf26d6f88a68dcdd426abc93ff4bc88c295546c89b7664b4d755e4d; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1667031457,1667110630,1667397227,1667635316; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1667635359; _lxsdk_s=18446ed730a-1f4-b1-22f%7C%7C1',
    'Referer': 'https://www.maoyan.com/board/4?offset=40',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


def get_resp(url):
	try:
		resp = requests.get(url, cookies=cookies, headers=headers)
		if resp.status_code == 200:
			return resp.text
		return None
	except RequestException:
		return None


def	parse_resp(html):
	pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?<img data-src="(.*?)".*?name"><a'
                         +'.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
                         +'.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
	items = re.findall(pattern, html)
	for item in items:
		yield  {
			'index': item[0],
			'image': item[1],
			'title': item[2],
			'actor': item[3].strip()[3:],
			'time': item[4].strip()[5:],
			'score': item[5]+item[6]
			}


def save_data(content):
	with open('result.txt', 'a', encoding='utf-8') as f:
		f.write(json.dumps(content, ensure_ascii=False) + '\n')


def main(page):
	url = 'https://www.maoyan.com/board/4?offset={}'.format(page)
	resp_text =get_resp(url)
	for item in parse_resp(resp_text):
		print(item)
		save_data(item)


if __name__ == "__main__":
	pool = Pool()
	pool.map(main, [i*10 for i in range(10)])