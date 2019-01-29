# coding=utf-8
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
import datetime
import codecs
from random import randint

"""https://bet.hkjc.com/football/getJSON.aspx?jsontype=index.aspx"""


homeScoreOddlist = {
    "S0100": "1_0",
    "S0200": "2_0",
    "S0201": "2_1",
    "S0300": "3_0",
    "S0301": "3_1",
    "S0302": "3_2",
    "S0400": "4_0",
    "S0401": "4_1",
    "S0402": "4_2",
    "S0500": "5_0",
    "S0501": "5_1",
    "S0502": "5_2",
    "SM1MH": "others",
}
awayScoreOddlist = {
    "S0001": "1_0",
    "S0002": "2_0",
    "S0102": "2_1",
    "S0003": "3_0",
    "S0103": "3_1",
    "S0203": "3_2",
    "S0004": "4_0",
    "S0104": "4_1",
    "S0204": "4_2",
    "S0005": "5_0",
    "S0105": "5_1",
    "S0205": "5_2",
    "SM1MA": "others",
}

drawScoreOddlist = {
    "S0000": "0_0",
    "S0101": "1_1",
    "S0202": "2_2",
    "S0303": "3_3",
    "SM1MD": "others",
}

def jsonCheck(m):
    try:
        return json.loads(m)
    except:
        return 2


def sessionGet():
    sessionUrl = "https://bet.hkjc.com/football/"
    s = requests.Session()
    s.get(sessionUrl)
    return s


def accessUrl(url, failCount):
    s = sessionGet()
    time.sleep(randint(0, 9))
    rawResult = s.get(url)
    if jsonCheck(rawResult.content) is not 2:
        return rawResult.content
    else:
        print "-----------"
        print "FailCount now is %s :(" % failCount
        print "-----------"
        if failCount > 5:
            return 2
        failCount = failCount + 1
        time.sleep(randint(1, 5))
        return accessUrl(url, failCount)

def matchDetails(matchId,failCount):
    url = "https://bet.hkjc.com/football/getJSON.aspx?jsontype=last_odds.aspx&matchid=%s" % matchId
    returnResult = accessUrl(url, failCount)
    return returnResult



"""Get confirmed mathc list"""

initUrl = "https://bet.hkjc.com/football/getJSON.aspx?jsontype=index.aspx"
initResult = accessUrl(initUrl, 0)
if initResult == 2:
    print "Init Fail."
    exit()
initResult = json.loads(initResult)
matchCount = 0
matchJson = []
for i in initResult:
    matchJson.append(i)
    print "NO %s, %s %s vs %s %s" % (matchCount,i["league"]["leagueNameCH"],i["homeTeam"]["teamNameCH"],i["awayTeam"]["teamNameCH"],i["matchTime"])
    matchCount = matchCount + 1
    if matchCount == 10:
        matchNo = raw_input("Match No?")
        if str(matchNo) == 'n':
            matchCount = 0
            matchJson = []
            continue
        matchId =  matchJson[int(matchNo)]["matchID"]
        """Print match odds"""
        matchJson = matchDetails(matchId,0)
        if matchJson == 2:
            print "Fail"
            exit()
        handicap = {}
        scoreOdds = {
            "home": {},
            "draw": {},
            "away": {},
        }
        euroOdds = {}
        matchJson = json.loads(matchJson)
        #Euro
        if "hadodds" in matchJson:
            euroOdds["home"] = re.findall("@(\d+.\d{1,2})", matchJson["hadodds"]["H"])[0]
            euroOdds["draw"] = re.findall("@(\d+.\d{1,2})", matchJson["hadodds"]["D"])[0]
            euroOdds["away"] = re.findall("@(\d+.\d{1,2})", matchJson["hadodds"]["A"])[0]
        print euroOdds

        # Asia Handicap
        if "hdcodds" in matchJson:
            handicap["home"] = re.findall("@(\d+.\d{1,2})", matchJson["hdcodds"]["H"])[0]
            handicap["away"] = re.findall("@(\d+.\d{1,2})", matchJson["hdcodds"]["A"])[0]
            # Handicap["Handicap"] = matchJson["hdcodds"]["AG"]
            HG = str(matchJson["hdcodds"]["HG"]).split("/")
            handicap["homeHandicap"] = float((float(HG[0]) + float(HG[1])) / 2)
        else:
            handicap = None

        # Score Odds
        if "crsodds" in matchJson:
            for (k, v) in homeScoreOddlist.iteritems():
                scoreOdds["home"][v] = re.findall("@(\d+.\d{1,2})", matchJson["crsodds"][k])[0]
            for (k, v) in awayScoreOddlist.iteritems():
                scoreOdds["away"][v] = re.findall("@(\d+.\d{1,2})", matchJson["crsodds"][k])[0]
            for (k, v) in drawScoreOddlist.iteritems():
                scoreOdds["draw"][v] = re.findall("@(\d+.\d{1,2})", matchJson["crsodds"][k])[0]

        homeScoreProb, drawScoreProb, awayScoreProb = 0.00, 0.00, 0.00
        for (k, v) in scoreOdds["home"].iteritems():
            homeScoreProb = homeScoreProb + (1 / float(v))
        for (k, v) in scoreOdds["draw"].iteritems():
            drawScoreProb = drawScoreProb + (1 / float(v))
        for (k, v) in scoreOdds["away"].iteritems():
            awayScoreProb = awayScoreProb + (1 / float(v))

        summary = {
            "league": matchJson["league"]["leagueShortName"],
            "homeTeam": matchJson["homeTeam"]["teamNameCH"],
            "awayTeam": matchJson["awayTeam"]["teamNameCH"],
            "matchTime": re.findall("(\d+-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2})", matchJson["matchTime"])[0].replace("T",
                                                                                                                " "),
            "euro": euroOdds,
            "asia": handicap,
            "prob": {
                "home": homeScoreProb,
                "draw": drawScoreProb,
                "away": awayScoreProb,
            }
        }
        print(json.dumps(summary, indent=4, sort_keys=False, encoding='UTF-8', ensure_ascii=False))

        """"""
        continueStatus = raw_input("continue, y or n?")
        if str(continueStatus) == "n":
            exit()
        matchCount = 0
        matchJson = []


