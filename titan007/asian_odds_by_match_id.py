# coding=utf-8
import sys
import os

projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(projectPath)
sys.stdout.reconfigure(encoding='utf-8')

import requests
import datetime
import re
import time
from config import connector
import utils.handicap as h
import argparse

c = connector.config()
match_id_list = range(49051,49062 +1)

matchResult = c.getMatchByIdIn(match_id_list)
print(matchResult)

# exit()
headers = {
    'referer': "http://live.titan007.com/indexall_big.aspx",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
}

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
    print(url)

    result = requests.get(url, headers=headers)
    # print(result.text)
    time.sleep(1)
    # grab all odds
    oddsRegex = r"<tr align=\"center\">(.*?)<\/tr>"
    oddsPattern = re.compile(oddsRegex, re.S)
    oddsResult = oddsPattern.findall(result.text)
    details = []
    for i in oddsResult:
        companyOddRegex = r"<td.*?>(.*?)<\/td>"
        companyOddPattern = re.compile(companyOddRegex, re.S)
        companyOddResult = companyOddPattern.findall(i)
        print(companyOddResult)
        details.append(companyOddResult)
    print("Details companyOddResult", details)
    for record in details:
        companyID = None
        handicap = None
        decimalHandicap = None
        homeOdds = None
        awayOdds = None
        result = None
        dateTime = None
        for i in range(len(record)):
            if (i < 12 and len(record[i]) > 1):
                companyID = i
                # print(record[i])
                singleOddRowRegex = r"(.*?)<br\s+\/>.*?<span.*?>(.*?)<\/span>.*?<span.*?>(.*?)<\/span>"
                singleOddRowPattern = re.compile(singleOddRowRegex, re.S)
                singleOddRowResult = singleOddRowPattern.findall(record[i])
                print("singleOddRowResult")
                print(len(singleOddRowResult))
                if len(singleOddRowResult) < 1:
                    continue
                handicap = singleOddRowResult[0][0]
                homeOdds = singleOddRowResult[0][1]
                awayOdds = singleOddRowResult[0][2]
                print("raw handicap: ", handicap)
                if handicap in h.handicapDict:
                    decimalHandicap = h.handicapDict[handicap]
                else:
                    continue
        if len(record) < 2:
            continue
        result = record[12]
        if len(result) < 1:
            result = None
        # print(record[13])
        rowDateRegex = r"(.*?)<br\s*\/>(.*?)$"
        rowDatePattern = re.compile(rowDateRegex, re.S)
        # rowDateResult = rowDatePattern.findall(record[13])
        rawDateResult = record[13]
        dateResult = re.split('\s', rawDateResult)
        # print(rowDateResult)
        oddUpdateDateTime = f"{matchYear}-{dateResult[0]} {dateResult[1]}"

        # print(oddUpdateDateTime)
        unixOddUpdateDateTime = int(
            time.mktime(datetime.datetime.strptime(oddUpdateDateTime, "%Y-%m-%d %H:%M").timetuple()))

        if unixOddUpdateDateTime > match[2] and result is None:
            newMatchYear = season[0]
            oddUpdateDateTime = f"{newMatchYear}-{dateResult[0]} {dateResult[1]}"
            unixOddUpdateDateTime = int(
                time.mktime(datetime.datetime.strptime(oddUpdateDateTime, "%Y-%m-%d %H:%M").timetuple()))

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
