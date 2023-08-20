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


# get matchID
currentDate = datetime.datetime.today().strftime("%Y-%m-%d 23:59:59")
print(currentDate)
print(type(currentDate))
# print(datetime.today().strftime("%Y-%m-%d 23:59:59").timetuple())
# int(time.mktime(datetime.strptime(match[3], "%Y-%m-%d %H:%M").timetuple()))
print(int(time.mktime(datetime.datetime.strptime(currentDate, "%Y-%m-%d 23:59:59").timetuple())))
currentDateUnixDate = int(time.mktime(datetime.datetime.strptime(currentDate, "%Y-%m-%d 23:59:59").timetuple()))

# Custom date
startTime = int(time.mktime(datetime.datetime.strptime("2021-05-20 00:00", "%Y-%m-%d %H:%M").timetuple()))
endTime = int(time.mktime(datetime.datetime.strptime("2023-10-27 23:59", "%Y-%m-%d %H:%M").timetuple()))

currentDate = datetime.datetime.now().strftime(f"%Y-%m-%d %H:00:00")
last7Days = (datetime.datetime.today() - datetime.timedelta(2)).strftime("%Y-%m-%d 23:59:59")
last7DaysUnixTime = int(time.mktime(datetime.datetime.strptime(last7Days, "%Y-%m-%d %H:%M:%S").timetuple()))

todayUnixTime = int(time.mktime(datetime.datetime.strptime(currentDate, "%Y-%m-%d %H:%M:%S").timetuple()))



c = connector.config()
matchResult = c.getMatchWithIn(currentDateUnixDate)
# matchResult = c.getMatchByLeagueId(75)
# matchResult = c.getMatchByLeagueIdAndSeason(279, "2021-2022")
# matchResult = c.getMatchByLeagueIdAndTime(279,startTime,endTime)
# matchResult = c.getMatchByBetweenTime(startTime, endTime)
# matchResult = c.getMatchByID(41027)

headers = {
    'referer': "http://live.titan007.com/indexall_big.aspx",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
}

def getContent(url):
    return url


for match in matchResult:
    print("match Date:", match[2], "match ID:", match[0])
    matchYear = datetime.datetime.utcfromtimestamp(match[2]).strftime("%Y")
    matchMonth = datetime.datetime.utcfromtimestamp(match[2]).strftime("%m")
    season = match[3].split("-")
    print(matchYear)
    print(matchMonth)
    outsideMatchId = match[1]
    previousOddList = []
    previousOddResult = c.findOddsByMatchID(match[0])
    previousOddList = [f"{x[0]}_{x[1]}_{str(x[2]).replace('.', '')}_{x[3]}" for x in previousOddResult]
    forSaveOddList = []
    # print("1527_10_075_1662633310" in previousOddList)
    # exit()

    # outsideMatchId = "2144035"
    url = f"https://vip.titan007.com/AsianOdds_n.aspx?id={outsideMatchId}"

    # result = requests.get(url, headers=headers)
    print(getContent(url))
    print(url)


    result = requests.get(url, headers=headers)
    # print(result.text)
    # exit()
    # print(result.text)
    time.sleep(2)
    # grab all odds
    oddsRegex = r"<tr align=\"center\" bgcolor=\"#ffffff\">(.*?)<\/tr>"
    oddsPattern = re.compile(oddsRegex, re.S)
    oddsResult = oddsPattern.findall(result.text)
    details = []
    for i in oddsResult:
        # print(i)
        # exit()
        # companyOddRegex = r"<td\s+style\=.*?>(.*?)<br\s\/>.*?<span.*?>(.*?)<\/span>.*?<span.*?>(.*?)<\/span><\/td>.*?(?:<td[\s|\s+]?.*?>(\d+-\d+)<\/td>.*?<td>(\d+-\d+)<br\/>(.*?)<\/td>|<td>(\d+-\d+)<br\/>(.*?)<\/td>)"
        companyOddRegex = r"<td.*?>(.*?)<\/td>"
        companyOddPattern = re.compile(companyOddRegex, re.S)
        companyOddResult = companyOddPattern.findall(i)
        # print(companyOddResult)
        details.append(companyOddResult)

    for record in details:
        companyID = None
        handicap = None
        decimalHandicap = None
        homeOdds = None
        awayOdds = None
        result = None
        dateTime = None
        for i in range(len(record)):
            if(i<12 and len(record[i])>1):
                companyID = i
                # print(record[i])
                singleOddRowRegex = r"(.*?)<br\s+\/>.*?<span.*?>(.*?)<\/span>.*?<span.*?>(.*?)<\/span>"
                singleOddRowPattern = re.compile(singleOddRowRegex, re.S)
                singleOddRowResult = singleOddRowPattern.findall(record[i])
                handicap = singleOddRowResult[0][0]
                homeOdds = singleOddRowResult[0][1]
                awayOdds = singleOddRowResult[0][2]
                print("raw handicap: ", handicap)
                if handicap in h.handicapDict:
                    decimalHandicap = h.handicapDict[handicap]
                else:
                    continue

        result = record[12]
        if len(result)<1:
            result = None
        # print(record[13])
        rowDateRegex = r"(.*?)<br\s*\/>(.*?)$"
        rowDatePattern = re.compile(rowDateRegex, re.S)
        rowDateResult = rowDatePattern.findall(record[13])
        # print(rowDateResult)
        oddUpdateDateTime = f"{matchYear}-{rowDateResult[0][0]} {rowDateResult[0][1]}"

        # print(oddUpdateDateTime)
        unixOddUpdateDateTime = int(time.mktime(datetime.datetime.strptime(oddUpdateDateTime, "%Y-%m-%d %H:%M").timetuple()))

        if unixOddUpdateDateTime > match[2] and result is None:
            newMatchYear = season[0]
            oddUpdateDateTime = f"{newMatchYear}-{rowDateResult[0][0]} {rowDateResult[0][1]}"
            unixOddUpdateDateTime = int(time.mktime(datetime.datetime.strptime(oddUpdateDateTime, "%Y-%m-%d %H:%M").timetuple()))


        list = (
            match[0],
            companyID,
            handicap,
            decimalHandicap,
            homeOdds,
            awayOdds,
            result,
            unixOddUpdateDateTime,
            int(time.time()),
            int(time.time())
        )
        # print(list)
        # print(f"{match[0]}_{companyID}_{str('%.2f' % decimalHandicap).replace('.', '')}_{unixOddUpdateDateTime}")
        # print("decimalHandicap",decimalHandicap)
        # print("companyID",companyID)
        # print("decimalHandicap",decimalHandicap)
        # print("decimalHandicap 2",str('%.2f' % decimalHandicap).replace('.', ''))
        # print("unixOddUpdateDateTime",unixOddUpdateDateTime)
        oddKey = f"{match[0]}_{companyID}_{str('%.2f' % decimalHandicap).replace('.', '')}_{unixOddUpdateDateTime}"
        # print(oddKey in previousOddList)

        if oddKey in previousOddList:
            continue
        forSaveOddList.append(list)

    # print("forSaveOddList")
    print(forSaveOddList)

    c.insertManyOdd(forSaveOddList)

        # oddResult = c.checkOddsExist(match[0],companyID,decimalHandicap, unixOddUpdateDateTime, homeOdds, awayOdds)
        # if oddResult is not None:
        #     continue
        # # exit()
        # c.insertOdd(list)