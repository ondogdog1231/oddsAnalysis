# coding=utf-8
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
import datetime
import codecs
from random import randint


class montherCrawler(threading.Thread):


    def __init__(self):
        super(montherCrawler).__init__()
        self.url = None
        self.json = None
        self.failCount = 0
        self.dateStart = self.dateEnd = None

    def jsonCheck(self,rawJson):
        try:
            return json.loads(rawJson)
        except:
            return 2

    def sessionGet(self):
        sessionUrl = "https://bet.hkjc.com/football/"
        s = requests.Session()
        s.get(sessionUrl)
        return s

    def accessUrl(self,url,failCount):
        s = self.sessionGet()
        time.sleep(randint(0, 9))
        rawResult = s.get(self.url)
        if self.jsonCheck(rawResult.content) is not 2:
            return rawResult.content
        else:
            print "-----------"
            print "FailCount now is %s :(" % self.failCount
            print "-----------"
            if self.failCount > 5:
                return 2
            self.failCount = self.failCount + 1
            time.sleep(randint(1, 5))
            return self.accessUrl(self.url, self.failCount)

    def pageDetail(self,pageNo):
        for i in pageNo:
            print i

    def run(self):
        try:
            self.json = self.accessUrl(self.url)
        except KeyboardInterrupt:
            print 'exiting main stock '
            exit()

yearList = [
    "2018",
    "2017",
    "2016",
    "2015",
    "2014",
    "2013",
    "2012",
]

monthList = [
    [
        "01",
        "0101",
        "0131",
    ],
    [
        "02",
        "0201",
        "0228",
    ],
    [
        "03",
        "0301",
        "0331",
    ],
    [
        "04",
        "0401",
        "0430",
    ],
    [
        "05",
        "0501",
        "0531",
    ],
    [
        "06",
        "0601",
        "0630",
    ],
    [
        "07",
        "0701",
        "0731",
    ],
    [
        "08",
        "0801",
        "0831",
    ],
    [
        "09",
        "0901",
        "0930",
    ],
    [
        "10",
        "1001",
        "1031",
    ],
    [
        "11",
        "1101",
        "1130",
    ],

    [
        "12",
        "1201",
        "1231",
    ],

]
"""
1. Get all year first page, record the total no of record
2. Get each year record
"""

if __name__ == "__main__":
    count = 0
    for year in yearList:
        for month in monthList:
            if os.path.isdir("./matchResult/%s-%s/" % (year, month[0])) is False:
                os.mkdir("./matchResult/%s-%s/" % (year, month[0]))
                print "file Make."
            mc = montherCrawler()
            mc.dateStart = month[1]
            mc.dateEnd = month[2]
            mc.year = year
            mc.url = "https://bet.hkjc.com/football/getJSON.aspx?jsontype=search_result.aspx&startdate=%s%s&enddate=%s%s&teamid=default&pageno=%s" % (
            year, month[1], year, month[2], 1)
            mc.run()


            # Each Month sleep 30 seconds

    """
        start a class for each month,  
    """


    # mc = montherCrawler()
