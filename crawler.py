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



# url = "http://odds.500.com/fenxi/ouzhi-731106.shtml?cids=3,280"
# Odds
# url = "http://odds.500.com/fenxi1/json/ouzhi.php?_=1547730329930&fid=731106&cid=3&r=1&time=2019-01-01+22%3A25%3A15&type=europe"
#asia
"""http://odds.500.com/fenxi1/inc/yazhiajax.php?fid=731111&id=4&t=1547731877918&r=1"""

sourceUrl = """http://odds.500.com/fenxi/yazhi-731111.shtml?cids=3"""

headers = {
'Pragma': 'no-cache',
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh,en-US;q=0.9,en;q=0.8,zh-TW;q=0.7',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
'Content-Type': 'application/x-www-form-urlencoded',
'Accept': 'application/json, text/javascript, */*',
'Cache-Control': 'no-cache',
'X-Requested-With': 'XMLHttpRequest'
}
url = "http://liansai.500.com/zuqiu-4826/"
"""
    Get all EPL Match
"""
r = requests.get(url,headers = headers)
print r.content.decode("gbk").encode("utf-8")
exit()








result = requests.get("""http://odds.500.com/fenxi1/inc/yazhiajax.php?fid=731111&id=3&t=1547732755883&r=1""",headers= headers)

resultJson = json.loads(result.content)
for i in resultJson:
    print i.replace("&nbsp;","")
exit()

url = """http://odds.500.com/fenxi1/inc/yazhiajax.php?fid=731111&id=3&t=1547732755883&r=1"""
r = requests.get(url,headers=headers)
print r
print r.content
exit()

content = r.content.decode("gbk").encode("utf-8")

print content
exit()
f = open("./result.txt", "w+")
f.write(content)
f.close()
