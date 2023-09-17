import sys
import os

projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
r = sys.path.append(projectPath)
sys.stdout.reconfigure(encoding='utf-8')

import requests
from datetime import datetime
import re
import json
import time
from config import connector
# 

now = datetime.now()
dateFormat = "%Y%m%d%H"
#format datetime using strftime()
currentDate = now.strftime(dateFormat)
print("current date: %s" % currentDate)
# Grab match info by season

seasons = [
    "2018-2019",
    "2019-2020",
    "2020-2021",
    "2021-2022",
    "2022-2023",
]
league = 9
leagueType = "league"
subClass = 0

for season in seasons:
    referer = f"http://info.titan007.com/cn/League/{season}/{league}.html"

    headers = {
        'referer': referer,
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
    }
    if leagueType != "cup":
        url = f"http://info.titan007.com/jsData/matchResult/{season}/s{league}.js?version={currentDate}"
    else:
        url = f"http://zq.titan007.com/jsData/matchResult/{season}/c{league}.js?version={currentDate}"


    if leagueType == "league":
        getSubClassUrl = f"https://zq.titan007.com/cn/SubLeague/{season}/{league}.html"
        print("getSubClassUrl",getSubClassUrl)
        subClassResult = requests.get(getSubClassUrl, headers=headers, allow_redirects=True)
        subClassRegex = r"var\s*SubSclassID\s*\=\s*(\d+);"
        pattern = re.compile(subClassRegex, re.S)
        subClassRegexResult = pattern.findall(subClassResult.text)
        if(len(subClassRegexResult)>0):
            subClass = int(subClassRegexResult[0])

    if subClass != 0:
        print("Has subClssID!!")
        url = f"https://zq.titan007.com/jsData/matchResult/{season}/s{league}_{subClass}.js?version={currentDate}"
    print(url)
    print("subClass",subClass)


    result = requests.get(url, headers=headers)
    regex = r"jh.*?\=.*?(\[\[.*?\]\]);"
    if leagueType == "cup":
        regex = r"jh\[\"G.*?\"\].*?\=.*?(\[\[.*?\]\]);"
    print (result.status_code)
    print(len(result.text))


    matchList = []
    requestCount = 0
    while (len(result.text)<10):
        if(requestCount<5):
            print("request count: %s", requestCount)
            result = requests.get(url, headers=headers)
            requestCount +=1
        else:
            exit("reach max tried")


    if(len(result.text)>=10):
        # print(result.text)
        pattern = re.compile(regex,re.S)
        regexResult = pattern.findall(result.text)

        for item in regexResult:
            # print(item)
            newItem = None
            try:
                newItem1 = item.replace("'", "\"")
                # print(newItem1)
                newItem = re.sub(r"\,\W\,", ",\"\"," ,newItem1)
                # print (newItem)
                jsonResult = json.loads(newItem)
                # exit(jsonResult)
                matchList.append(jsonResult)
            except Exception as e:
                print ("In exception")
                print(str(e))
                print (newItem)
            # else:
            #     # print ("OKOK")

        c = connector.config()
        for item in matchList:
            # exit(item)
            for match in item:
                print("len(match)")
                print(len(match))
                print(match)
                # Since cup match will return aggregate result
                if(len(match)<10):
                    match = [item for item in match if type(item) is list]
                    print(match)
                    exit()
                    continue
                #Check exist
                getMatch = c.getMatch(match[0])
                if getMatch is not None:
                    print(getMatch[0], match[7], match[6])
                    c.updateMatchResult(getMatch[0], match[7], match[6])
                    continue
                else:
                    print(f"match {match[0]} not exist")
                print(match)
                print(match[0])
                print(match[3])
                #0 matchID , 1 league ID, 3 date, 4,5,6 result, 7 half time result, 8 home rank, 9 away rank
                list = (
                    match[0],
                    season,
                    match[1],
                    match[3],
                    int(time.mktime(datetime.strptime(match[3], "%Y-%m-%d %H:%M").timetuple())),
                    match[7],
                    match[6],
                    match[4],
                    match[5],
                    int(time.time()),
                    int(time.time())
                )
                print(list)
                c.inserMatch(list)
    else:
        print("Content is null")

    time.sleep(5)
