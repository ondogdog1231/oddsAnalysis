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
            "bigSamll": "big" if float(int(matchJson["accumulatedscore"][1]["home"]) + int(matchJson["accumulatedscore"][1]["away"])) > 2.5 else "small"
        }



        print json.dumps(summary, indent=4, sort_keys=False, encoding='UTF-8', ensure_ascii=False)
        if summary["asia"] is None:
            continue

        p = predictionModel(
            summary["asia"]["homeHandicap"],
            round_down(summary["prob"]["home"],2),
            round_down(summary["prob"]["home"],2)+0.01,
            round_down(summary["prob"]["away"], 2),
            round_down(summary["prob"]["home"], 2) + 0.01,
            0,1000,0,1000)
        returnResult = p.prediction()
        print returnResult
        print float(returnResult["small"]) / float(returnResult["fileCount"])
        print float(returnResult["big"]) / float(returnResult["fileCount"])


        exit()
        testFileNameList.append(summary)

print(json.dumps(testFileNameList, indent=4, sort_keys=False, encoding='UTF-8', ensure_ascii=False))








