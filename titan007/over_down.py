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

parser = argparse.ArgumentParser(description='Asian Odds')
parser.add_argument('leagueId', type=int, help="League ID")
args = parser.parse_args()

c = connector.config()
league_id = args.leagueId
# matchResult = c.getMatchByLeagueId(league_id)
matchResult = c.getMatchByID(25352)

headers = {
    'referer': "http://live.titan007.com/indexall_big.aspx",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
}

for match in matchResult:
    print("match Date:", match[2], "match ID:", match[0])
    datetime_utc = datetime.datetime.utcfromtimestamp(match[2])
    datetime_hkt = datetime_utc + datetime.timedelta(hours=8)
    # matchYear = datetime.datetime.utcfromtimestamp(match[2]).strftime("%Y")
    # matchMonth = datetime.datetime.utcfromtimestamp(match[2]).strftime("%m")
    matchYear = datetime_hkt.year
    matchMonth = datetime_hkt.month
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
    url = f"http://vip.titan007.com/changeDetail/overunder.aspx?id={outsideMatchId}&companyID=3&l=1"

    # result = requests.get(url, headers=headers)
    print(f"url :{url}")

    result = requests.get(url, headers=headers)
    # print(result.text)
    time.sleep(1)
    # grab all odds
    oddsRegex = r"<TR align=center .*?>(.*?)<\/tr>"
    oddsPattern = re.compile(oddsRegex, re.MULTILINE | re.IGNORECASE | re.DOTALL | re.S)
    oddsResult = oddsPattern.findall(result.text)

    if len(oddsResult) < 1:
        exit("odds content is null")

    oddsResult = oddsResult[1:]
    rowResult = []
    for i in oddsResult:
        rowResult.append(i)

    for i in rowResult:
        pattern = r'<td.*?>(.*?)<\/td>.*?<td.*?>(.*?)<\/td>.*?<td.*?>.*?<b>(.*?)<\/b>.*?<td.*?font.*?>(.*?)<\/td>.*?<b>(.*?)<\/b>.*?<td.*?>(.*?)<\/td>'
        # Use re.findall() to find all matches
        matches = re.findall(pattern, i, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        print(matches)
        if len(matches) < 1:
            continue
        dataResult = matches[0]
        dateResult = re.split('\s', dataResult[5])
        oddsUpdateTime = f"{matchYear}-{dateResult[0]} {dateResult[1]}"
        print(f"oddsUpdateTime {oddsUpdateTime}")
        unixOddUpdateDateTime = int(
            time.mktime(datetime.datetime.strptime(oddsUpdateTime, "%Y-%m-%d %H:%M").timetuple()))
        datetime_utc = datetime.datetime.utcfromtimestamp(unixOddUpdateDateTime)
        datetime_hkt = datetime_utc + datetime.timedelta(hours=8)
        formatted_date_hkt = datetime_hkt.strftime("%Y-%m-%d %H:%M:%S HKT")
        print(f"Before any action: {formatted_date_hkt}")
        print(f"{unixOddUpdateDateTime}, {match[2]}")
        print(f"unixOddUpdateDateTime > match[2] :{unixOddUpdateDateTime > match[2]}")
        if unixOddUpdateDateTime > match[2]:
            newMatchYear = season[0]
            print(f"newMatchYear {newMatchYear}")
            oddUpdateDateTime = f"{newMatchYear}-{dateResult[0]} {dateResult[1]}"
            print(f"oddUpdateDateTime {oddUpdateDateTime}")
            unixOddUpdateDateTime = int(
                time.mktime(datetime.datetime.strptime(oddUpdateDateTime, "%Y-%m-%d %H:%M").timetuple()))
        datetime_utc = datetime.datetime.utcfromtimestamp(unixOddUpdateDateTime)
        datetime_hkt = datetime_utc + datetime.timedelta(hours=8)
        formatted_date_hkt = datetime_hkt.strftime("%Y-%m-%d %H:%M:%S HKT")
        print(formatted_date_hkt)
        print("\n")

    exit()
