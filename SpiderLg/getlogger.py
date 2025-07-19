# coding:utf-8

# @Author: WWB
# @CurrentFile: getlogger.py
# @DateTime: 2019/5/4 12:50


import logging


def getlogger():
    logger = logging.getLogger("test.conf")
    logger.setLevel(logging.DEBUG)
    hterm = logging.StreamHandler()
    hterm.setLevel(logging.ERROR)
    hfile = logging.FileHandler("access.log")
    hfile.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    hterm.setFormatter(formatter)
    hfile.setFormatter(formatter)

    logger.addHandler(hterm)
    logger.addHandler(hfile)

    return logger
