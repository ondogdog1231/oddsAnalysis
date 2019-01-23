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
        time.sleep(randint(9, 20))
        return accessUrl(url, failCount)


for fileNames in os.listdir("./matchResult"):
    print fileNames
    if fileNames == "20180101_20180131_page_26.json":
        continue

    matchList = []
    with codecs.open("./matchResult/%s" % fileNames, 'r', encoding='utf8') as f:
        text = f.read()
    a = json.loads(text)

    for i in a[0]["matches"]:
        print i["matchID"]
        matchList.append(i["matchID"])

    for id in matchList:
        failCount = 0
        url = "https://bet.hkjc.com/football/getJSON.aspx?jsontype=last_odds.aspx&matchid=%s" % (id)
        returnResult = accessUrl(url, failCount)
        print returnResult
        pathName = "./matchDetailResult/%s.json" % (id,)
        f = open(pathName, "w+")
        print "----------------------"
        print returnResult
        f.write(returnResult)
        f.close()
