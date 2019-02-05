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
from predictionModel import predictionModel
import math

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


def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier


# p = predictionModel(0.75,0.74,0.75,0.37,0.38,0,1000,0,1000)
# returnResult = p.prediction()
# print returnResult["fileCount"]
# exit()

with codecs.open('./prediction201901.json', 'r', encoding='utf8') as f:
    text = f.read()

resultJson = json.loads(text)
handicapCount = 0
handicapCountWin = 0
handicapCountLose = 0
bigSmallCount = 0
bigSmallCountWin = 0
bigSmallCountLose = 0
print len(resultJson)
for item in resultJson:
    # print json.dumps(item["prediction"])
    if abs(item["asia"]["homeHandicap"]) != 0.75:
        continue

    if item["prediction"]["result"]["handicap"] is not None:
        handicapCount += 1
    if item["prediction"]["result"]["handicap"] == True:
        handicapCountWin +=1
    if item["prediction"]["result"]["handicap"] == False:
        handicapCountLose +=1

    if item["prediction"]["result"]["smallBig"] is not None:
        bigSmallCount += 1
    if item["prediction"]["result"]["smallBig"] == True:
        bigSmallCountWin +=1
    if item["prediction"]["result"]["smallBig"] == False:
        bigSmallCountLose +=1




print "Win %s, Lose %s / %s" %(bigSmallCountWin,bigSmallCountLose,bigSmallCount)
print "Win %s, Lose%s / %s" %(handicapCountWin,handicapCountLose,handicapCount)

exit()

"""
    1. Get the result, probability,odds
    
    2. Match the probability,range + 0.01
    
    3. Separate 3 Level, 
        i) Match probability
        ii) Match Asia Level +/- 0.5
        iii) Match Euro Level +/- 0.5
    
    4. 
      File Count more than 6                 
       level_1_handicap  result
       level_2_handicap  result
       level_3_handicap  result
    
    5. 
       level_1_bigSmall  result
       level_2_bigSmall  result
       level_3_bigSmall  result
    
    WinBetCount and LoseBet
    
"""
testFileNameList = []

for root, subdirs, files in os.walk("../matchDetailResult/2019-01"):

    for fileName in files:
        """Reset Variable"""
        matchJson = None
        handicap = {}
        scoreOdds = {
            "home": {},
            "draw": {},
            "away": {},
        }
        euroOdds = {}
        homeScoreProb, drawScoreProb, awayScoreProb = 0.00, 0.00, 0.00
        path = "%s/%s" % (root, fileName)

        with codecs.open(path, 'r', encoding='utf8') as f:
            text = f.read()
        matchJson = json.loads(text)
        # print path
        # print matchJson["matchStatus"]
        if str(matchJson["matchStatus"]) == "Canceled":
            continue
        # print(json.dumps(matchJson, indent=4, sort_keys=False, encoding='UTF-8', ensure_ascii=False))
        # print re.findall("@(\d+.\d{1,2})", matchJson["hadodds"]["H"])[0]
        # exit()
        if "hadodds" in matchJson:
            euroOdds["home"] = re.findall("@(\d+.\d{1,2})", matchJson["hadodds"]["H"])[0]
            euroOdds["draw"] = re.findall("@(\d+.\d{1,2})", matchJson["hadodds"]["D"])[0]
            euroOdds["away"] = re.findall("@(\d+.\d{1,2})", matchJson["hadodds"]["A"])[0]


            # Asia Handicap
        if "hdcodds" in matchJson:
            handicap["home"] = re.findall("@(\d+.\d{1,2})", matchJson["hdcodds"]["H"])[0]
            handicap["away"] = re.findall("@(\d+.\d{1,2})", matchJson["hdcodds"]["A"])[0]

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
            },
            "homeScore": int(matchJson["accumulatedscore"][1]["home"]),
            "awayScore": int(matchJson["accumulatedscore"][1]["away"]),
            "bigSamll": "big" if float(int(matchJson["accumulatedscore"][1]["home"]) + int(
                matchJson["accumulatedscore"][1]["away"])) > 2.5 else "small"
        }

        # print json.dumps(summary, indent=4, sort_keys=False, encoding='UTF-8', ensure_ascii=False)

        if summary["asia"] is None:
            continue

        p = predictionModel(
            summary["asia"]["homeHandicap"],
            round_down(summary["prob"]["home"], 3),
            round_down(summary["prob"]["home"], 3) + 0.01,
            round_down(summary["prob"]["away"], 3),
            round_down(summary["prob"]["away"], 3) + 0.01,
            0, 1000, 0, 1000)
        returnResult = p.prediction()
        if returnResult is None:
            # print returnResult
            continue
        if int(returnResult["fileCount"]) < 9:
            continue
        # print returnResult
        smallPrediction = float(returnResult["small"]) / float(returnResult["fileCount"])
        bigPrediction = float(returnResult["big"]) / float(returnResult["fileCount"])
        summary["prediction"] = {
            "smallBig":None,
            "handicap":None,
            "result":{
                "smallBig":None,
                "handicap":None
            }
        }
        if smallPrediction > 0.68 or bigPrediction > 0.68:
            summary["prediction"]["smallBig"] = "small" if smallPrediction > bigPrediction else "big"
            if summary["prediction"]["smallBig"] == summary["bigSamll"]:
                summary["prediction"]["result"]["smallBig"] = True
            else:
                summary["prediction"]["result"]["smallBig"] = False


        upPrediction = float(returnResult["upHalf"]+returnResult["upCount"])/float(returnResult["fileCount"])
        downPrediction = float(returnResult["downWinHalf"]+returnResult["downCount"])/float(returnResult["fileCount"])
        # print upPrediction
        # print downPrediction
        if upPrediction > 0.65 or downPrediction > 0.65:
            result = None
            summary["prediction"]["handicap"] = "up" if upPrediction > smallPrediction else "down"
            if float(summary["asia"]["homeHandicap"]) < 0.0:
                if summary["homeScore"] + summary["asia"]["homeHandicap"] - summary["awayScore"]:
                    result = "up"
                else:
                    result = "down"
            if float(summary["asia"]["homeHandicap"]) > 0.0:
                if summary["homeScore"] + summary["asia"]["homeHandicap"] - summary["awayScore"]:
                    result = "down"
                else:
                    result = "up"
            if summary["asia"]["homeHandicap"] == 0.0:
                if summary["homeScore"] - summary["awayScore"]:
                    result = "up"
                else:
                    result = "down"

            if result == summary["prediction"]["handicap"]:
                summary["prediction"]["result"]["handicap"] = True
            else:
                summary["prediction"]["result"]["handicap"] = False

        if summary["prediction"]["smallBig"] is not None or summary["prediction"]["handicap"] is not None:
            print json.dumps(summary, indent=4, sort_keys=False, encoding='UTF-8', ensure_ascii=False)
            testFileNameList.append(summary)

fileName = "./%s.json" % "prediction201901"
f = open(fileName, "w+")
f.write(str(json.dumps(testFileNameList, indent=4, sort_keys=False, encoding='UTF-8', ensure_ascii=False).encode('utf-8')))
f.close()