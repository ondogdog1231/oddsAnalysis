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
import collections

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
up_half = 0
downWinHalf = 0

bigSmallCount = {
    "score_0": 0,
    "score_1": 0,
    "score_2": 0,
    "score_3": 0,
    "score_4": 0,
    "score_5": 0,
    "score_6": 0,
}

fileCount = 0
hot_1_5_Count = 0
hot_1_6_Count = 0
hot_1_7_Count = 0
hot_1_8_Count = 0
fileNameList = []
probList = []
probCountList = {
    "c_0.81": 0,
    "c_0.82": 0,
    "c_0.83": 0,
    "c_0.84": 0,
    "c_0.85": 0,
    "c_0.86": 0,
    "c_0.87": 0,
    "c_0.88": 0,
    "c_0.89": 0,
    "c_0.9": 0,
    "c_0.91": 0,
    "c_0.92": 0,
    "c_0.93": 0,
    "c_0.94": 0,
    "c_0.95": 0,
    "c_0.96": 0,
    "c_0.97": 0,
    "c_0.98": 0,
    "c_0.99": 0,
    "c_1.0": 0,
    "c_1.01": 0,
    "c_1.02": 0,
    "c_1.03": 0,
    "c_1.04": 0,
    "c_1.05": 0,
    "c_1.06": 0,
    "c_1.07": 0,
    "c_1.08": 0,
    "c_1.09": 0,
    "c_1.10": 0,
    "c_1.11": 0,
    "c_1.12": 0,
    "c_1.13": 0,
    "c_1.14": 0,
    "c_1.15": 0,
    "c_1.16": 0,
    "c_1.17": 0,
    "c_1.18": 0,
    "c_1.19": 0,
    "c_1.2": 0,
    "c_1.21": 0,
    "c_1.23": 0,
}

for root, subdirs, files in os.walk("../matchDetailResult"):

    for fileName in files:
        path = "%s/%s" % (root, fileName)
        # if "2018-03" not in path:
        #     continue
        fileNameList.append(path)
# print fileNameList
# exit()
customHandicap = float(raw_input("Asia?"))
lowerLimit = float(raw_input("lower Limit ?"))
upperLimit = float(raw_input("Upper Limit ?"))
secondLowerLimit = float(raw_input("Second Lower Limit ?"))
secondUpperLimit = float(raw_input("Second Upper Limit ?"))
# Odds
asiaOddsLowerLimit = float(raw_input("Asia Odds Lower Limit ?"))
asiaOddsUpperLimit = float(raw_input("Asia Odds Upper Limit ?"))
# Odds
euroOddsLowerLimit = float(raw_input("Euro Odds Lower Limit ?"))
euroOddsUpperLimit = float(raw_input("Euro Odds Upper Limit ?"))

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
    # Big Small
    # bigSmall = 0
    #
    # if matchJson["hilodds"] is not None:
    #     if matchJson["hilodds"]["LINELIST"] is not None:
    #         for item in matchJson["hilodds"]["LINELIST"]:
    #             bigSmallItem = item["LINE"].split("/")
    #             bigSmall = (float(bigSmallItem[0]) + float(bigSmallItem[1]))/2

    summary = {
        "league": matchJson["league"]["leagueShortName"],
        "matchId": matchJson["matchID"],
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


    if summary["asia"] is not None:

        if summary["asia"]["homeHandicap"] == -customHandicap and customHandicap != 0:
            if summary["homeScore"] + -customHandicap - summary["awayScore"] > 0.0:
                summary["asiaResult"] = "UP"
                if customHandicap == 0.75 and summary["homeScore"] + -customHandicap - summary["awayScore"] < 1.0:
                    summary["asiaResult"] = "UP_HALF"
            elif summary["homeScore"] + -customHandicap - summary["awayScore"] == 0.0:
                summary["asiaResult"] = "RUN"
            else:
                summary["asiaResult"] = "DOWN"

        if summary["asia"]["homeHandicap"] == customHandicap and customHandicap != 0:
            if summary["homeScore"] + customHandicap - summary["awayScore"] > 0.0:
                summary["asiaResult"] = "DOWN"
                if customHandicap == 0.25 and summary["homeScore"] + customHandicap - summary["awayScore"] == 0.25:
                    summary["asiaResult"] = "DOWN_WIN_HALF"
            elif summary["homeScore"] + customHandicap - summary["awayScore"] == 0.0:
                summary["asiaResult"] = "RUN"
            elif summary["homeScore"] + customHandicap - summary["awayScore"] < 0.0:
                summary["asiaResult"] = "UP"
                if customHandicap == 0.75 and 0 < summary["homeScore"] + customHandicap - summary["awayScore"] < 1.0:
                    summary["asiaResult"] = "UP_HALF"

        if summary["asia"]["homeHandicap"] == customHandicap and customHandicap == 0:

            if summary["homeScore"] - summary["awayScore"] > 0:
                summary["asiaResult"] = "UP"
            if summary["homeScore"] - summary["awayScore"] < 0:
                summary["asiaResult"] = "DOWN"
            if summary["homeScore"] - summary["awayScore"] == 0:
                summary["asiaResult"] = "RUN"


        if ((lowerLimit <= float(summary["prob"]["home"]) <= upperLimit) or (lowerLimit <= float(summary["prob"]["away"]) <= upperLimit)) \
                and ((secondLowerLimit <= float(summary["prob"]["home"]) <= secondUpperLimit) or ((secondLowerLimit <= float(summary["prob"]["away"]) <= secondUpperLimit))) \
                and ((asiaOddsLowerLimit <= float(summary["asia"]["home"]) <= asiaOddsUpperLimit) or (asiaOddsLowerLimit <= float(summary["asia"]["away"]) <= asiaOddsUpperLimit))\
                and ((euroOddsLowerLimit <= float(summary["euro"]["home"]) <= euroOddsUpperLimit) or (euroOddsLowerLimit <= float(summary["euro"]["away"]) <= euroOddsUpperLimit))\
                and ((summary["asia"]["homeHandicap"] == customHandicap) or (summary["asia"]["homeHandicap"] == -customHandicap)):

            # print(json.dumps(summary, indent=4, sort_keys=False, encoding='UTF-8', ensure_ascii=False))

            if summary["asiaResult"] is "UP":
                upCount = upCount + 1
            if summary["asiaResult"] is "UP_HALF":
                up_half = up_half + 1
            if summary["asiaResult"] is "DOWN":
                downCount = downCount + 1

            if summary["asiaResult"] is "DOWN_WIN_HALF":
                downWinHalf = downWinHalf + 1

            if summary["asiaResult"] is "RUN":
                runCount = runCount + 1

            if summary["homeScore"] + summary["awayScore"] < 6:
                bigSmallCount["score_%s" % str(summary["homeScore"] + summary["awayScore"])] += 1
            else:
                bigSmallCount["score_6"] += 1

            fileCount = fileCount + 1

            print(json.dumps(summary, indent=4, sort_keys=False, encoding='UTF-8', ensure_ascii=False))

print "File count: %s" % fileCount
print "Up count(上盤): %s, %s" % (upCount, ((float(upCount) / float(fileCount)) * 100)) + "%"
print "HALF count(上盤): %s, %s " % (up_half, ((float(up_half) / float(fileCount)) * 100)) + "%"
print "Down count(下盤): %s, %s " % (downCount, ((float(downCount) / float(fileCount)) * 100)) + "%"
print "Down_WIN_HALF count(下盤): %s ,%s" % (downWinHalf, ((float(downWinHalf) / float(fileCount)) * 100)) + "%"
print "Run count: %s, %s" % (runCount, ((float(runCount) / float(fileCount)) * 100)) + "%"

totalBigSmallCount = sum(bigSmallCount.values())
print "--------------------"

for (k, v) in bigSmallCount.iteritems():
    print "Score %s: %s " % (k, float(float(v) / float(totalBigSmallCount)) * 100) + "%"

smallPercentage = (float(bigSmallCount["score_0"] + bigSmallCount["score_1"] + bigSmallCount["score_2"]) / float(
    totalBigSmallCount) * 100)

bigPercentage = (float(
    bigSmallCount["score_3"] + bigSmallCount["score_4"] + bigSmallCount["score_5"] + bigSmallCount["score_6"]) / float(
    totalBigSmallCount) * 100)

print "Small: %s" % smallPercentage
print "Big: %s" % bigPercentage

# probList.sort()
# print json.dumps(probList, indent=4, sort_keys=False, encoding='UTF-8', ensure_ascii=False)
# probCountList.sort()
# print probCountList
