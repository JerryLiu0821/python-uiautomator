#coding=utf-8
import os
import re
import logging

#logging.basicConfig(level=logging.DEBUG)

"""logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='debug.log',
    filemode='w')"""


def _format(message, level, tag):
    return '\n'.join(['[%d][%s]: %s'%(level, tag, msg) for msg in message.splitlines()])

def debug(message, tag="DEBUG"):
    logging.debug(_format(message, logging.DEBUG, tag))

def warning(message, tag="WARNING"):
    logging.warning(_format(message, logging.WARNING, tag))

def info(message, tag="INFO"):
    logging.info(_format(message, logging.INFO, tag))

def error(message, tag="ERROR"):
    logging.error(_format(message, logging.ERROR, tag))

def log_directory():
    return "."

def report_directory():
    return "."

def procrank():
    return 'procrank.log'

def dumpsys_meminfo():
    return 'dumpsys_meminfo.log'

def meminfo():
    return 'proc_meminfo.log'

def kernel():
    return 'kmsg.log'

def logcat():
    return 'logcat_main.log'

def uiautomator():
    return 'uiautomator.log'

def top():
    return 'top.log'

def total_pss():
    return 'total_pss.svg'

def top_10_pss():
    return 'top_10_pss.svg'

def save_pic_path():
    return '/data/local/tmp/hometest'
