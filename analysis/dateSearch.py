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

homeScoreOddlist = {
    "S0100": "1_0",
    "S0200": "2_0",
    "S0201": "2_1",
    "S0300": "3_0",
    "S0301": "3_1",
    "S0302": "3_2",
    "S0400": "4_0",
    "S0401": "4_1",
    "S0402": "4_2",
    "S0500": "5_0",
    "S0501": "5_1",
    "S0502": "5_2",
    "SM1MH": "others",
}
awayScoreOddlist = {
    "S0001": "1_0",
    "S0002": "2_0",
    "S0102": "2_1",
    "S0003": "3_0",
    "S0103": "3_1",
    "S0203": "3_2",
    "S0004": "4_0",
    "S0104": "4_1",
    "S0204": "4_2",
    "S0005": "5_0",
    "S0105": "5_1",
    "S0205": "5_2",
    "SM1MA": "others",
}

drawScoreOddlist = {
    "S0000": "0_0",
    "S0101": "1_1",
    "S0202": "2_2",
    "S0303": "3_3",
    "SM1MD": "others",
}


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
            return 2
        failCount = failCount + 1
        time.sleep(randint(1, 5))
        return accessUrl(url, failCount)


# Get the result list
dateStart = str(raw_input("dateStart: "))
dateEnd = str(raw_input("dateEnd: "))

indexUrl = "https://bet.hkjc.com/football/getJSON.aspx?jsontype=search_result.aspx&startdate=%s&enddate=%s&teamid=default&pageno=%s" % (
dateStart, dateEnd,1)
listResult = json.loads(accessUrl(indexUrl, 0))
matchCount = int(listResult[0]["matchescount"])
pageTotal = int(math.ceil(float(matchCount / 20.0)))


for i in listResult[0]["matches"]:
    print "ID: %s, %s vs %s, %s:%s  " % (
    i["matchID"], i["homeTeam"]["teamNameCH"], i["awayTeam"]["teamNameCH"], i["accumulatedscore"][1]["home"],
    i["accumulatedscore"][1]["away"])


if pageTotal > 1:
    for i in range(2,pageTotal +1):
        print "--------------page %s--------------" % i
        indexUrl = "https://bet.hkjc.com/football/getJSON.aspx?jsontype=search_result.aspx&startdate=%s&enddate=%s&teamid=default&pageno=%s" % (
            dateStart, dateEnd, i)
        listResult = json.loads(accessUrl(indexUrl, 0))
        for i in listResult[0]["matches"]:
            print "ID: %s, %s vs %s, %s:%s  " % (
                i["matchID"], i["homeTeam"]["teamNameCH"], i["awayTeam"]["teamNameCH"],
                i["accumulatedscore"][1]["home"],
                i["accumulatedscore"][1]["away"])
