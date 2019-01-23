import sys
import os

import requests
import re
import time
import threading
from datetime import datetime
import hashlib

import json
# from library.bs4 import BeautifulSoup
from bs4 import BeautifulSoup
import math

import codecs

from random import randint



with codecs.open("20180101_20180131_result.json", 'r', encoding='utf8') as f:
    text = f.read()

a = json.loads(text)

matchCount = int(a[0]["matchescount"])
print matchCount
pageTotal = int(math.ceil(float(matchCount / 20.0)))
print pageTotal


def jsonCheck(m):
    try:
        return json.loads(m)
    except:
        return 2


def sessionGet():
    sessionUrl = "https://bet.hkjc.com/football/"
    s = requests.Session()
    s.get(sessionUrl)
    return s


def accessUrl(url, failCount):
    s = sessionGet()
    time.sleep(randint(0, 9))
    rawResult = s.get(url)
    if jsonCheck(rawResult.content) is not 2:
        return rawResult.content
    else:
        print "-----------"
        print "FailCount now is %s :(" % failCount
        print "-----------"
        if failCount > 5:
            return "Fail"
        failCount = failCount + 1
        time.sleep(randint(0, 9))
        return accessUrl(url, failCount)


for i in range(11, pageTotal + 1):
    failCount = 0
    startDate = "20180101"
    endDate = "20180131"
    url = "https://bet.hkjc.com/football/getJSON.aspx?jsontype=search_result.aspx&startdate=%s&enddate=%s&teamid=default&pageno=%s" % (
        startDate, endDate, i)
    returnResult = accessUrl(url, failCount)
    print returnResult
    pathName = "./matchResult/20180101_20180131_page_%s.json" % (i)
    f = open(pathName, "w+")
    print "----------------------"
    print returnResult
    f.write(returnResult)
    f.close()

