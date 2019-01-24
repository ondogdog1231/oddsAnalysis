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
upCount = 0
downCount = 0
runCount = 0
fileCount = 0
hot_1_5_Count = 0
hot_1_6_Count = 0
hot_1_7_Count = 0
hot_1_8_Count = 0
fileNameList = []
probList = []
probCountList = {
    "c_0.81" : 0,
    "c_0.82" : 0,
    "c_0.83" : 0,
    "c_0.84" : 0,
    "c_0.85" : 0,
    "c_0.86" : 0,
    "c_0.87" : 0,
    "c_0.88" : 0,
    "c_0.89" : 0,
    "c_0.9" : 0,
    "c_0.91" : 0,
    "c_0.92" : 0,
    "c_0.93" : 0,
    "c_0.94" : 0,
    "c_0.95" : 0,
    "c_0.96" : 0,
    "c_0.97" : 0,
    "c_0.98" : 0,
    "c_0.99" : 0,
    "c_1.0" : 0,
    "c_1.01" : 0,
    "c_1.02" : 0,
    "c_1.03" : 0,
    "c_1.04" : 0,
    "c_1.05" : 0,
    "c_1.06" : 0,
    "c_1.07" : 0,
    "c_1.08" : 0,
    "c_1.09" : 0,
    "c_1.10" : 0,
    "c_1.11" : 0,
    "c_1.12" : 0,
    "c_1.13" : 0,
    "c_1.14" : 0,
    "c_1.15" : 0,
    "c_1.16" : 0,
    "c_1.17" : 0,
    "c_1.18" : 0,
    "c_1.19" : 0,
    "c_1.2" : 0,
    "c_1.21" : 0,
    "c_1.23" : 0,
}

for root, subdirs, files in os.walk("../matchDetailResult"):

    for fileName in files:
        path = "%s/%s" % (root, fileName)
        # if "2018-03" not in path:
        #     continue
        fileNameList.append(path)
# print fileNameList
# exit()

for filenames in fileNameList:

    handicap = {}
    scoreOdds = {
        "home": {},
        "draw": {},
        "away": {},
    }
    euroOdds = {}
    with codecs.open(filenames, 'r', encoding='utf8') as f:
        text = f.read()

    matchJson = json.loads(text)

    # print "%s vs %s" % (matchJson["homeTeam"]["teamNameCH"], matchJson["awayTeam"]["teamNameCH"])

    if matchJson["matchStatus"] != "ResultIn":
        # print "%s vs %s" % (matchJson["homeTeam"]["teamNameCH"], matchJson["awayTeam"]["teamNameCH"])
        # print "is canceled"
        continue
    # Euro Odds
    if "hadodds" in matchJson:
        euroOdds["home"] = re.findall("@(\d+.\d{1,2})", matchJson["hadodds"]["H"])[0]
        euroOdds["draw"] = re.findall("@(\d+.\d{1,2})", matchJson["hadodds"]["D"])[0]
        euroOdds["away"] = re.findall("@(\d+.\d{1,2})", matchJson["hadodds"]["A"])[0]

    # Asia Handicap
    if "hdcodds" in matchJson:
        handicap["HomeOdds"] = re.findall("@(\d+.\d{1,2})", matchJson["hdcodds"]["H"])[0]
        handicap["AwayOdds"] = re.findall("@(\d+.\d{1,2})", matchJson["hdcodds"]["A"])[0]
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
        "league" : matchJson["league"]["leagueShortName"],
        "homeTeam": matchJson["homeTeam"]["teamNameCH"],
        "awayTeam": matchJson["awayTeam"]["teamNameCH"],
        "matchTime": re.findall("(\d+-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2})", matchJson["matchTime"])[0].replace("T", " "),
        "euro": euroOdds,
        "asia": handicap,
        "prob": {
            "home": homeScoreProb,
            "draw": drawScoreProb,
            "away": awayScoreProb,
        },
        "homeScore": int(matchJson["accumulatedscore"][1]["home"]),
        "awayScore": int(matchJson["accumulatedscore"][1]["away"]),
    }
    customHandicap = 0.25
    if summary["asia"] is not None:
        if summary["asia"]["homeHandicap"] == -customHandicap:
            if summary["homeScore"] + -customHandicap - summary["awayScore"] > 0.0:
                summary["asiaResult"] = "UP"
            elif summary["homeScore"] + -customHandicap - summary["awayScore"] == 0.0:
                summary["asiaResult"] = "RUN"
            else:
                summary["asiaResult"] = "DOWN"

        if summary["asia"]["homeHandicap"] == customHandicap:
            if summary["homeScore"] + customHandicap - summary["awayScore"] > 0.0:
                summary["asiaResult"] = "DOWN"
            elif summary["homeScore"] + customHandicap - summary["awayScore"] == 0.0:
                summary["asiaResult"] = "RUN"
            else:
                summary["asiaResult"] = "UP"
    # fileCount = fileCount + 1
    if summary["asia"] is not None and abs(summary["asia"]["homeHandicap"]) == customHandicap:
        # print(json.dumps(summary, indent=4, sort_keys=False, encoding='UTF-8', ensure_ascii=False))

        if max(summary["prob"]["home"],summary["prob"]["away"]) not in probList:
            probList.append(max(summary["prob"]["home"],summary["prob"]["away"]))
        # print probCountList["c_%s" % round(max(summary["prob"]["home"],summary["prob"]["away"]),2)]
        # probCountList["c_%s" % round(max(summary["prob"]["home"],summary["prob"]["away"]),2)] = probCountList["c_%s" % round(max(summary["prob"]["home"],summary["prob"]["away"]),2)]+ 1
        fileCount = fileCount + 1
        continue

        """ 0.75 """
        lowerLimit = 0.83
        upperLimit = 0.84
        # if (float(summary["prob"]["draw"]) >= 0.3):

        if ((lowerLimit  <= float(summary["prob"]["home"]) <= upperLimit) or (lowerLimit <= float(summary["prob"]["away"]) <= upperLimit))\
                and \
            ((0.29 <= float(summary["prob"]["home"]) <= 0.30) or (0.29 <= float(summary["prob"]["away"]) <= 0.30)):
             # and \
                # ((1.51 <= float(summary["euro"]["home"]) <= 1.53) or (1.51 <= float(summary["euro"]["away"]) <= 1.53))\

            # print(json.dumps(summary, indent=4, sort_keys=False, encoding='UTF-8', ensure_ascii=False))

            if summary["asiaResult"] is "UP":
                upCount = upCount + 1
                # print "%s-%s" % (summary["homeScore"],summary["awayScore"])

            if summary["asiaResult"] is "DOWN":
                downCount = downCount + 1
            if summary["asiaResult"] is "RUN":
                runCount = runCount + 1
            fileCount = fileCount + 1
            print(json.dumps(summary, indent=4, sort_keys=False, encoding='UTF-8', ensure_ascii=False))

print "File count: %s" % fileCount
print "Up count(上盤): %s" % upCount
print "Down count(下盤): %s" % downCount
print "Run count: %s" % runCount
probList.sort()
print json.dumps(probList, indent=4, sort_keys=False, encoding='UTF-8', ensure_ascii=False)
# probCountList.sort()
# print probCountList
