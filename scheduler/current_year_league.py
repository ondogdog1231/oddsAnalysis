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
import argparse
import subprocess

c = connector.config()


class getLeague:
    def __init__(self, leagueType, league, season):
        self.league = league
        self.season = season
        self.leagueType = leagueType
        referer = f"http://info.titan007.com/cn/League/{season}/{league}.html"
        self.headers = {
            'referer': referer,
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
        }

    def checkMatchExist(self, outSideLeagueId):
        getMatch = c.getMatch(outSideLeagueId)
        if getMatch is not None:
            return True
        return False

    def checkHasSubClass(self, matchList):
        returnMatchList = []
        for match in matchList:
            if type(match) is list:
                returnMatchList.append(match)
        if len(returnMatchList) > 0:
            return returnMatchList
        else:
            return matchList

    def checkSubLeague(self, content):
        subLeague = []
        regex = r"var\s*arrSubLeague\s*\=(.*?)\;"
        pattern = re.compile(regex, re.S)
        regexResult = pattern.findall(content)
        if len(regexResult) == 0:
            return
        tempResult = regexResult[0]
        tempResult = tempResult.replace("'", "\"")
        tempResult = re.sub(r"\,\W\,", ",\"\",", tempResult)
        jsonResult = json.loads(tempResult)
        for j in jsonResult:
            subLeague.append(j[0])
        return subLeague

    def generateSubClassUrl(self, subClassId):
        now = datetime.now()
        dateFormat = "%Y%m%d%H"
        currentDate = now.strftime(dateFormat)
        return f"https://zq.titan007.com/jsData/matchResult/{self.season}/s{self.league}_{subClassId}.js?version={currentDate}"

    def getMatch(self):
        now = datetime.now()
        dateFormat = "%Y%m%d%H"
        currentDate = now.strftime(dateFormat)
        subClass = 0
        if self.leagueType != "cup":
            url = f"http://info.titan007.com/jsData/matchResult/{self.season}/s{self.league}.js?version={currentDate}"
        else:
            url = f"http://zq.titan007.com/jsData/matchResult/{self.season}/c{self.league}.js?version={currentDate}"
        if self.leagueType == "league":
            getSubClassUrl = f"https://zq.titan007.com/cn/SubLeague/{self.season}/{self.league}.html"
            print("getSubClassUrl", getSubClassUrl)
            subClassResult = requests.get(getSubClassUrl, headers=self.headers, allow_redirects=True)
            subClassRegex = r"var\s*SubSclassID\s*\=\s*(\d+);"
            pattern = re.compile(subClassRegex, re.S)
            subClassRegexResult = pattern.findall(subClassResult.text)
            if (len(subClassRegexResult) > 0):
                subClass = int(subClassRegexResult[0])

        if subClass != 0:
            print("Has subClssID!!")
            url = f"https://zq.titan007.com/jsData/matchResult/{self.season}/s{self.league}_{subClass}.js?version={currentDate}"

        return url

    def grabMatch(self):
        result = requests.get(self.url, headers=self.headers)
        print(result.status_code)
        print(len(result.text))
        requestCount = 0
        while (len(result.text) < 10):
            if (requestCount < 5):
                print("request count: %s", requestCount)
                result = requests.get(self.url, headers=self.headers)
                print(f"Retrying - {requestCount}")
                requestCount += 1
            else:
                exit("reach max tried")
        return result.text

    def getMatchDeatilFromRegex(self, leagueType,content):
        regex = r"jh.*?\=.*?(\[\[.*?\]\]);"
        if leagueType == "cup":
            regex = r"jh\[\"G.*?\"\].*?\=.*?(\[\[.*?\]\]);"
        pattern = re.compile(regex, re.S)
        regexResult = pattern.findall(content)
        return regexResult

    def formatMatch(self, regexResult):
        matchList = []
        for item in regexResult:
            # print(item)
            newItem = None
            try:
                newItem1 = item.replace("'", "\"")
                # print(newItem1)
                newItem = re.sub(r"\,\W\,", ",\"\",", newItem1)
                newItem = re.sub(r"\=\"(.*?)\"", "=''", newItem)
                # print (newItem)
                jsonResult = json.loads(newItem)
                # exit(jsonResult)
                matchList.append(jsonResult)
            except Exception as e:
                print("In exception")
                print(str(e))
                print("newItem1", newItem1)
                print(newItem)
        return matchList

    def checkExist(self, match):
        # if match[0] != 2397002:
        #     exit("in match 2397002")
        #     return False
        getMatch = c.getMatch(match[0])

        halfTimeResult = len(match[7]) > 0 and match[7] or None
        fullTimeResult = len(match[6]) > 0 and match[6] or None
        print(f"halfTime: {halfTimeResult}, fullTime: {fullTimeResult}")

        raw_date_time = match[3]

        unix_time = int(time.mktime(datetime.strptime(match[3], "%Y-%m-%d %H:%M").timetuple()))
        if getMatch is not None:
            # if getMatch[0] == 41027:
            #     print("41027",halfTimeResult,fullTimeResult)
            #     print("41027", match[4],match[5])
            #     exit()
            #     return False
            c.updateMatchResultAndTime(getMatch[0], match[4],
                                       match[5], halfTimeResult, fullTimeResult, raw_date_time,
                                       unix_time)
            return True
        else:
            return False

    def checkMatchExistAndInsert(self, matchList):
        i = 0
        for match in matchList:
            i += 1
            print("index", i)
            print("Len: ", len(match))
            print("match in checkMatchExistAndInsert", match)
            print("match in checkMatchExistAndInsert", match[0])
            # print("self.checkExist(match)", self.checkExist(match))
            # print("halfTimeResult:", match[7])
            # print("fullTimeResult:", match[6])
            try:
                if len(match) > 10:
                    if self.checkExist(match) is False:
                        self.insertMatch(match)
                else:
                    for item in match:
                        if type(item) == list:
                            if self.checkExist(item) is False:
                                self.insertMatch(item)
            except Exception as e:
                print("In exception")
                print(str(e))
                print("error matchList", matchList)
                print("error item", match)

    def insertMatch(self, match):
        print("time.mktime(datetime.strptime(match[3]")
        print(time.mktime(datetime.strptime(match[3], "%Y-%m-%d %H:%M").timetuple()))
        print("halfTimeResult:", match[7])
        print("fullTimeResult:", match[6])

        halfTimeResult = len(match[7]) > 0 and match[7] or None
        fullTimeResult = len(match[6]) > 0 and match[6] or None

        list = (
            match[0],
            season,
            match[1],
            match[3],
            int(time.mktime(datetime.strptime(match[3], "%Y-%m-%d %H:%M").timetuple())),
            halfTimeResult,
            fullTimeResult,
            match[4],
            match[5],
            int(time.time()),
            int(time.time())
        )
        # if match[0] is "2397002":
        #     print("list")
        #     print(list)
        #     exit()
        c.insertMatch(list)

    def main(self):
        self.url = self.getMatch()
        print(self.url)
        content = self.grabMatch()
        subLeagueIdList = self.checkSubLeague(content)
        matchList = []
        if subLeagueIdList is not None:
            for subClassId in subLeagueIdList:
                self.url = self.generateSubClassUrl(subClassId)
                print("subclass loop", self.url)
                content = self.grabMatch()
                regexResult = self.getMatchDeatilFromRegex(self.leagueType,content)
                # print(regexResult)
                matchList = self.formatMatch(regexResult)
                # print("matchList len",len(matchList))
                # print("matchList len 1",len(matchList[0]))
                # print("matchList ",(matchList[0]))
                newMatchList = []
                i = 0
                for item in matchList:
                    for match in item:
                        i += 1
                        print("index: ", i)
                        print("match in subClass:", match)
                        newMatchList.append(match)
                print(f"len(newMatchList): {len(newMatchList)}")
                self.checkMatchExistAndInsert(newMatchList)

            return
            # exit()
        else:
            regexResult = self.getMatchDeatilFromRegex(self.leagueType,content)
            matchList = self.formatMatch(regexResult)
        if len(matchList) == 0:
            return
        newMatchList = []
        for item in matchList:
            print("item 2")
            print("raw 2")
            print(item)
            print("item[0]")
            print(item[0])
            for i in item:
                if type(i) is list:
                    newMatchList.append(i)
            if type(item[0]) is not list:
                newMatchList.append(item)
        self.checkMatchExistAndInsert(newMatchList)


# JLeague
# seasons = [
#     "2017",
#     "2018",
#     "2019",
#     "2020",
#     "2021",
#     "2022",
#     "2023",
# ]


all_leagues_id = c.getLeagueIdInMatch()
for league_id_result in all_leagues_id:
    league_id = league_id_result[0]
    print(league_id)
    seasons = [
        "2023-2024",
        "2023",
        "2024"
    ]
    for season in seasons:
        crawler = getLeague("league", league_id, season)
        crawler.main()
    time.sleep(5)
odds_command = f"asian_odds.py"
