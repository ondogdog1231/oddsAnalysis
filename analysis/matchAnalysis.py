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
    "S0302": "3_1",
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
    "S0101": "1_1",
    "S0202": "2_2",
    "S0303": "3_3",
    "SM1MD": "others",
}

for filenames in os.listdir("../matchDetailResult"):
    print filenames
    handicap = {}
    scoreOdds = {
        "home": {},
        "draw": {},
        "away": {},
    }
    euroOdds = {}
    with codecs.open("../matchDetailResult/%s" % filenames, 'r', encoding='utf8') as f:
        text = f.read()

    matchJson = json.loads(text)

    # print "%s vs %s" % (matchJson["homeTeam"]["teamNameCH"], matchJson["awayTeam"]["teamNameCH"])

    if matchJson["matchStatus"] != "ResultIn":
        print "%s vs %s" % (matchJson["homeTeam"]["teamNameCH"], matchJson["awayTeam"]["teamNameCH"])
        print "is canceled"
        continue
    # Euro Odds
    if "hadodds" in matchJson:
        euroOdds["home"] = re.findall("@(\d+.\d{1,2})", matchJson["hadodds"]["H"])[0]
        euroOdds["draw"] = re.findall("@(\d+.\d{1,2})", matchJson["hadodds"]["D"])[0]
        euroOdds["away"] = re.findall("@(\d+.\d{1,2})", matchJson["hadodds"]["A"])[0]

    # Asia Handicap
    if "hdcodds" in matchJson:
        handicap["HomeOdds"] = matchJson["hdcodds"]["H"]
        handicap["AwayOdds"] = matchJson["hdcodds"]["A"]
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
        homeScoreProb = homeScoreProb + 1 / float(v)
    for (k, v) in scoreOdds["draw"].iteritems():
        drawScoreProb = drawScoreProb + 1 / float(v)
    for (k, v) in scoreOdds["away"].iteritems():
        awayScoreProb = awayScoreProb + 1 / float(v)


    summary = {
        "homeTeam": matchJson["homeTeam"]["teamNameCH"],
        "awayTeam": matchJson["awayTeam"]["teamNameCH"],
        "matchTime": matchJson["matchTime"],
        "euro": euroOdds,
        "asia": handicap,
        "prob": {
            "home": homeScoreProb,
            "draw": drawScoreProb,
            "away": awayScoreProb,
        },
        "homeScore": matchJson["accumulatedscore"][1]["home"],
        "awayScore": matchJson["accumulatedscore"][1]["away"],
    }

    if summary["asia"] is not None and abs(summary["asia"]["homeHandicap"]) == 0.25:
        print(json.dumps(summary, indent=4, sort_keys=False ,encoding='UTF-8', ensure_ascii=False))
