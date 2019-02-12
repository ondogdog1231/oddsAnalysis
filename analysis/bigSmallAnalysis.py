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

"""http://liansai.500.com/index.php?c=score&a=getmatch&stid=13195&round=21"""

handlinelist = {
    "球半",1.5
}



class oddsHandicap():
    def __init__(self, url):
        self.url = url

    def requestsFunc(self,url):
        r = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
                'referer': 'http://liansai.500.com/',
            })
        return r.content


    def dataCrawler(self):
        r = self.requestsFunc(self.url)
        result = json.loads(r)
        # print(json.dumps(result, indent=4, sort_keys=False, encoding='UTF-8', ensure_ascii=False))
        for item in result:
            print item["gname"]
            print item["hname"]
            print item["hscore"]
            print item["gscore"]
            print json.dumps(item, indent=4, sort_keys=False, encoding='UTF-8', ensure_ascii=False)
            url = "http://odds.500.com/fenxi/daxiao-%s.shtml?cids=5,3,280,9,293,8" % item["fid"]
            print url
            exit()
            detailResult = self.requestsFunc(url)
            # print detailResult.decode("gbk")
            print json.dumps(self.webGraber(detailResult))


    def webGraber(self,content):
        oddList = []
        print "start"
        # print content
        # regex = r"<tr\s+?.*?id=\"(.*?)\".*?\"ping\">(.*?)<\/td>.*?ref=\"(.*?)\""
        regex = r"<tr\s+class=\"tr1\".*?id=\"(.*?)\".*?class=\"ping\">(.*?)\<\/td>.*?ref=\"(.*?)\".*?\"ying\">(.*?)<\/td>.*?class=\"pl_table_data\".*?class=\"\">(.*?)<\/td>.*?ref=\"(.*?)\".*?<\/td>.*?class=\"\">(.*?)<\/td>"

        pattern = re.compile(regex
                             ,re.MULTILINE|re.DOTALL)
        # print pattern
        matches = pattern.findall(content)
        # print matches
        for item in matches:
            oddList.append({
                "id":item[0],
                "homeFinalOdds":item[1].replace("\xa1\xfd","").replace("\xa1\xfc",""),
                "handline":item[2],
                "awayFinalOdds":item[3].replace("\xa1\xfd","").replace("\xa1\xfc",""),
                "homeInitOdds":item[4],
                "handlineInit":item[5],
                "awayInitOdds":item[6],
            })
        return oddList


for i in range(1,39):
    odd = oddsHandicap("http://liansai.500.com/index.php?c=score&a=getmatch&stid=11944&round=%s"%i)
    odd.dataCrawler()
    time.sleep(1)
