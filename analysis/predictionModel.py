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




class predictionModel():

    def __init__(self,customHandicap, lowerLimit,upperLimit,secondLowerLimit,secondUpperLimit,asiaOddsLowerLimit,asiaOddsUpperLimit,euroOddsLowerLimit,euroOddsUpperLimit):
        self.upperLimit = float(upperLimit)
        self.lowerLimit = float(lowerLimit)
        self.secondUpperLimit = float(secondUpperLimit)
        self.secondLowerLimit = float(secondLowerLimit)
        self.customHandicap = float(customHandicap)
        self.asiaOddsLowerLimit = float(asiaOddsLowerLimit)
        self.asiaOddsUpperLimit = float(asiaOddsUpperLimit)
        self.euroOddsUpperLimit = float(euroOddsUpperLimit)
        self.euroOddsLowerLimit = float(euroOddsLowerLimit)

    def prediction(self):
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
        for root, subdirs, files in os.walk("../matchDetailResult"):

            for fileName in files:
                path = "%s/%s" % (root, fileName)

                if "2019-01" in path:
                    continue
                fileNameList.append(path)

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

            if matchJson["matchStatus"] != "ResultIn":
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
                "matchId": matchJson["matchID"],
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
            }

            if summary["asia"] is not None:

                if summary["asia"]["homeHandicap"] == -self.customHandicap:
                    if summary["homeScore"] + -self.customHandicap - summary["awayScore"] > 0.0:
                        summary["asiaResult"] = "UP"
                        if self.customHandicap == 0.75 and summary["homeScore"] + -self.customHandicap - summary[
                            "awayScore"] < 1.0:
                            summary["asiaResult"] = "UP_HALF"
                    elif summary["homeScore"] + -self.customHandicap - summary["awayScore"] == 0.0:
                        summary["asiaResult"] = "RUN"
                    else:
                        summary["asiaResult"] = "DOWN"

                if summary["asia"]["homeHandicap"] == self.customHandicap:
                    if summary["homeScore"] + self.customHandicap - summary["awayScore"] > 0.0:
                        summary["asiaResult"] = "DOWN"
                        if self.customHandicap == 0.25 and summary["homeScore"] + self.customHandicap - summary[
                            "awayScore"] == 0.25:
                            summary["asiaResult"] = "DOWN_WIN_HALF"
                    elif summary["homeScore"] + self.customHandicap - summary["awayScore"] == 0.0:
                        summary["asiaResult"] = "RUN"
                    elif summary["homeScore"] + self.customHandicap - summary["awayScore"] < 0.0:
                        summary["asiaResult"] = "UP"
                        if self.customHandicap == 0.75 and 0 < summary["homeScore"] + self.customHandicap - summary[
                            "awayScore"] < 1.0:
                            summary["asiaResult"] = "UP_HALF"
                if summary["asia"]["homeHandicap"] == self.customHandicap and self.customHandicap == 0:

                    if summary["homeScore"] - summary["awayScore"] > 0:
                        summary["asiaResult"] = "UP"
                    if summary["homeScore"] - summary["awayScore"] < 0:
                        summary["asiaResult"] = "DOWN"
                    if summary["homeScore"] - summary["awayScore"] == 0:
                        summary["asiaResult"] = "RUN"


                if ((self.lowerLimit <= float(summary["prob"]["home"]) <= self.upperLimit) or (self.lowerLimit <= float(summary["prob"]["away"]) <= self.upperLimit)) \
                        and ((self.secondLowerLimit <= float(summary["prob"]["home"]) <= self.secondUpperLimit) or (
                    (self.secondLowerLimit <= float(summary["prob"]["away"]) <= self.secondUpperLimit))) \
                        and ((summary["asia"]["homeHandicap"] == self.customHandicap) or (
                    summary["asia"]["homeHandicap"] == -self.customHandicap))\
                        and ((self.asiaOddsLowerLimit <= float(summary["asia"]["home"]) <= self.asiaOddsUpperLimit) or (
                            self.asiaOddsLowerLimit <= float(summary["asia"]["away"]) <= self.asiaOddsUpperLimit))\
                        and ((self.euroOddsLowerLimit <= float(summary["euro"]["home"]) <= self.euroOddsUpperLimit) or (
                                        self.euroOddsLowerLimit <= float(summary["euro"]["away"]) <= self.euroOddsUpperLimit)):
                    #     and ((summary["asia"]["homeHandicap"] == self.customHandicap) or (
                    # summary["asia"]["homeHandicap"] == -self.customHandicap)):

                    # print summary
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
                    # print(json.dumps(summary, indent=4, sort_keys= False, encoding='UTF-8', ensure_ascii=False))

        # print "File count: %s" % fileCount
        # print "Up count(上盤): %s, %s" % (upCount, ((float(upCount) / float(fileCount)) * 100)) + "%"
        # print "HALF count(上盤): %s, %s " % (up_half, ((float(up_half) / float(fileCount)) * 100)) + "%"
        # print "Down count(下盤): %s, %s " % (downCount, ((float(downCount) / float(fileCount)) * 100)) + "%"
        # print "Down_WIN_HALF count(下盤): %s ,%s" % (downWinHalf, ((float(downWinHalf) / float(fileCount)) * 100)) + "%"
        # print "Run count: %s, %s" % (runCount, ((float(runCount) / float(fileCount)) * 100)) + "%"
        #
        totalBigSmallCount = sum(bigSmallCount.values())
        # print "--------------------"
        #
        # for (k, v) in bigSmallCount.iteritems():
        #     print "Score %s: %s " % (k, float(float(v) / float(totalBigSmallCount)) * 100) + "%"
        #
        # smallPercentage = (
        # float(bigSmallCount["score_0"] + bigSmallCount["score_1"] + bigSmallCount["score_2"]) / float(
        #     totalBigSmallCount) * 100)
        #
        # bigPercentage = (float(
        #     bigSmallCount["score_3"] + bigSmallCount["score_4"] + bigSmallCount["score_5"] + bigSmallCount[
        #         "score_6"]) / float(
        #     totalBigSmallCount) * 100)
        #
        # print "Small: %s" % smallPercentage
        # print "Big: %s" % bigPercentage
        if fileCount == 0:
            return None
        predictionSummary = {
            "fileCount": fileCount,
            "upCount": upCount,
            "upHalf":up_half,
            "downCount": downCount,
            "downWinHalf": downWinHalf,
            "runCount": runCount,
            # "totalBigSmall": totalBigSmallCount,
            "small": (bigSmallCount["score_0"] + bigSmallCount["score_1"] + bigSmallCount["score_2"]),
            "big": (bigSmallCount["score_3"] + bigSmallCount["score_4"] + bigSmallCount["score_5"] + bigSmallCount[
                "score_6"])
        }
        return predictionSummary

