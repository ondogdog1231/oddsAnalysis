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

# def daterange(start_date, end_date):
#     if start_date != end_date:
#         for n in range((end_date - start_date).days + 1):
#             yield start_date + datetime.timedelta(n)
#     else:
#         for n in range((start_date - end_date).days + 1):
#             yield start_date - datetime.timedelta(n)
#
#
# start = datetime.date(year=2018, month=1, day=1)
# end = datetime.date(year=2018, month=4, day=1)
# print start
#
# for date in daterange(start, end):
#     print date
# exit()



dateList = [
    # ["20180101", "20180131"],
    # ["20180201", "20180228"],
    # ["20180301", "20180331"],
    # ["20180401", "20180430"],
    # ["20180501", "20180531"],
    # ["20180601", "20180630"],
    # ["20180701", "20180731"],
    # ["20180801", "20180831"],
    # ["20180901", "20180930"],
    # ["20181001", "20181031"],
    # ["20181101", "20181130"],
    # ["20181201", "20181231"],
    # ["20181201", "20181231"],
    ["20190101", "20190128"],
]

# for i in dateList:
#     print i[0]
#     print i[1]
# exit()


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


def accessUrl(url,failCount):
    s = sessionGet()
    time.sleep(2)
    rawResult = s.get(url)
    print rawResult.content
    if jsonCheck(rawResult.content) is not 2:
        return rawResult.content
    else:
        if failCount > 5:
            return "Fail"
        failCount = failCount + 1
        time.sleep(2)
        return accessUrl(url,failCount)



for i in dateList:
    failCount = 0
    startDate = i[0]
    endDate = i[1]
    url = "https://bet.hkjc.com/football/getJSON.aspx?jsontype=search_result.aspx&startdate=%s&enddate=%s&teamid=default" % (startDate,endDate)
    returnResult = accessUrl(url,0)

    pathName = "./pageJson/%s_%s_result.json" % (startDate,endDate)
    f = open(pathName, "w+")
    print "----------------------"
    print returnResult
    f.write(returnResult)
    f.close()





