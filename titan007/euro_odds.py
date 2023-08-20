# coding=utf-8
import sys
import os

projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(projectPath)
sys.stdout.reconfigure(encoding='utf-8')

import requests
# from datetime import datetime
import datetime
import re
import json
import time
from config import connector

matchId = 2222308
url = f"https://1x2d.titan007.com/{matchId}.js"
headers = {
    'referer': f"http://1x2.titan007.com/oddslist/{matchId}_2.htm",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
}
result = requests.get(url, headers=headers)

# print(result.text)
rawOddsRegex = r"var\sgameDetail\=Array\((.*?)\)\;"
oddsPattern = re.compile(rawOddsRegex, re.S)
oddsResult = oddsPattern.findall(result.text)
# print(oddsResult[0])


a = str(oddsResult[0]).split(",")
print(a)






