# coding=utf-8
import sys
import os
import time

projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(projectPath)
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json
from datetime import datetime
from config import connector
import re


c = connector.config()

now = datetime.now()
dateFormat = "%Y%m%d%H"
currentDate = now.strftime(dateFormat)

regex = r"teamDetail\s+\=\s+(\[.*?\])\;"

result = c.getAllAwayTeams()
result2 = c.getAllHomeTeams()
teamList = list(set(result + result2))

for team in teamList:
    team_id = team[0]
    if c.checkTeamsExist(team_id) is True:
        continue

    print(f"adding team: {team_id}")
    url = f"https://zq.titan007.com/jsData/teamInfo/teamDetail/tdl{team_id}.js?version={currentDate}"
    referer = f"https://zq.titan007.com/cn/team/Summary/{team_id}.html"

    headers = {
        'referer': referer,
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
    }
    result = requests.get(url, headers=headers)
    print(result.text)
    requestCount = 0


    # while(requestCount < 5 and len(result.text)<10):
    #     print(f"requestCount 2: {requestCount}")
    #     result = requests.get(url, headers=headers)
    #     requestCount += 1


    while(len(result.text)<10):
        print(f"requestCount 1: {requestCount}")

        if (requestCount < 5):
            time.sleep(3)
            print(f"requestCount 2: {requestCount}")
            result = requests.get(url, headers=headers)
            requestCount +=1
        else:
            print("reach max")
            continue



    pattern = re.compile(regex, re.S)
    regex_result = pattern.findall(result.text)
    if regex_result is None:
        print(f"{team_id} cant found")
        continue
    formatted_result = str(regex_result[0]).replace("\"",'').replace("'","\"")

    # print(formatted_result)
    jsonResult = json.loads(formatted_result)
    print(jsonResult[0],jsonResult[1],jsonResult[2],jsonResult[3])


#     Check team exist
    if c.checkTeamsExist(jsonResult[0]) is True:
        continue
#     Insert team
    list = (
        jsonResult[0],
        jsonResult[3],
        jsonResult[2],
        jsonResult[1],
        int(time.time()),
        int(time.time())

    )
    c.insertTeams(list)



exit()