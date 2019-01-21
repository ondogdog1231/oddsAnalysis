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

mylist = [x*x for x in range(3)]
for i in mylist:
    print(i)
""""""
exit()

def daterange(start_date, end_date):
    if start_date != end_date:
        for n in range((end_date - start_date).days + 1):
            yield start_date + datetime.timedelta(n)
    else:
        for n in range((start_date - end_date).days + 1):
            yield start_date - datetime.timedelta(n)


start = datetime.date(year=2010, month=1, day=1)
end = datetime.date(year=2018, month=2, day=1)
print start

for date in daterange(start, end):
    print date
exit()


def jsonCheck(m):
    try:
        json.loads(m)
        return 1
    except:
        return 2


def sessionGet():
    sessionUrl = "https://bet.hkjc.com/football/"
    s = requests.Session()
    sessionSet = s.get(sessionUrl)
    return s


failCount = 0

s = sessionGet()
time.sleep(1)
url = "https://bet.hkjc.com/football/getJSON.aspx?jsontype=search_result.aspx&startdate=20180101&enddate=20180131&teamid=default&pageno=40"

content = s.get(url)
resultJson = json.loads(content)
print resultJson.content
exit()

f = open("./result.txt", "w+")
f.write(resultJson.content)
f.close()
exit()
