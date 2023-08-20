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

currentHour = datetime.datetime.now().hour

currentDate = datetime.datetime.now().strftime(f"%Y-%m-%d %H:00:00")
last7Days = (datetime.date.today() - datetime.timedelta(7)).strftime("%Y-%m-%d 23:59:59")


last7DaysUnixTime = int(time.mktime(datetime.datetime.strptime(last7Days, "%Y-%m-%d %H:%M:%S").timetuple()))

todayUnixTime = int(time.mktime(datetime.datetime.strptime(currentDate, "%Y-%m-%d %H:%M:%S").timetuple()))

startTime = int(time.mktime(datetime.datetime.strptime("2022-10-23 00:00", "%Y-%m-%d %H:%M").timetuple()))
endTime = int(time.mktime(datetime.datetime.strptime("2022-10-24 23:59", "%Y-%m-%d %H:%M").timetuple()))


c = connector.config()

result = c.getMatchBetweenTime(startTime,endTime)


for match in result:

    url = f"http://zq.titan007.com/default/getScheduleInfo?sid={match[1]}&t=${todayUnixTime}000"
    referer = f"http://zq.titan007.com/analysis/{match[1]}.htm"
    headers = {
        'referer': referer,
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
    }
    print(url)
    matchResult = requests.get(url, headers=headers)
    regex = r"\[(.*)\]"
    pattern = re.compile(regex,re.S)
    regexResult = pattern.findall(matchResult.text)
    print(regexResult[0])
    if(len(regexResult[0])<1):
        continue
    print(regexResult[0].split(","))
    details = regexResult[0].split(",")
    fullTime = f"{details[1]}-{details[2]}"
    halfTime = f"{details[3]}-{details[4]}"
    c.updateMatchResult(match[0], halfTime, fullTime)
