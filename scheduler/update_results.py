# coding=utf-8
import sys
import os

projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(projectPath)
sys.stdout.reconfigure(encoding='utf-8')


import requests
import datetime
import re
import json
import time
from config import connector
import utils.handicap as h

print(f"start time: {datetime.datetime.now()}")
# get matchID
start_time = (datetime.datetime.now() - datetime.timedelta(hours=96)).strftime("%Y-%m-%d %H:00:00")

# start_time = datetime.datetime.today().strftime("%Y-%m-%d 00:00:00")
end_time = (datetime.datetime.today() + datetime.timedelta(days=0)).strftime("%Y-%m-%d 23:59:59")

unix_start_time = int(time.mktime(datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").timetuple()))
unix_end_time = int(time.mktime(datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").timetuple()))

currentDate = datetime.datetime.now().strftime(f"%Y-%m-%d %H:00:00")
todayUnixTime = int(time.mktime(datetime.datetime.strptime(currentDate, "%Y-%m-%d %H:%M:%S").timetuple()))

c = connector.config()

print(start_time,end_time)
print(unix_start_time,unix_end_time)

result = c.getMatchBetweenTime(unix_start_time,unix_end_time)



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
