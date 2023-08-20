# coding=utf-8
import sys
import os

projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(projectPath)
sys.stdout.reconfigure(encoding='utf-8')



import requests
# from datetime import datetime
import datetime
import re
import json
import time
from config import connector
from config import asianOddsConfig
import numpy as np
from numpy import genfromtxt

record_start_time = datetime.datetime.now()

print(f"start time: {record_start_time}")

asian_odd_config_classifiers = asianOddsConfig.config().model_list()



# print(asian_odd_config)
# Asian odds
"""
1. select work send time > current time and status == 0
- update status to processing  
2. group match by league ID
3. predict by league payload
4. create message
5. send ? 
"""
c = connector.config()
matchList = []
# schedulerResult = c.findScheduleJobsByNameAndStatus("asianPrediction")

works = c.findWorkBeforeTimeAndStatus(int(time.time()),0)
for work in works:
    print(work)
    matchList.append(work[2])
if len(matchList) <1:
    print("No match")
    exit()

matchDetails = c.getMatchDetailsByIdIn(matchList)
predictionMatchList = {}
for matchDetail in matchDetails:
    set = {
        "league_id":matchDetail[5],
        "time": matchDetail[7],
        "home_team": matchDetail[8],
        "away_team": matchDetail[9],
        "prediction": []
    }
    predictionMatchList[matchDetail[0]] = set

company_id = 1

oddsResult = c.findOddsByIdInAndCompanyId(company_id, matchList)

currentId = None
oddSummaryList = {}
for oddRow in oddsResult:
    matchId = oddRow[0]
    companyId = oddRow[1]
    decimalHandicap = oddRow[2]
    homeOdd = oddRow[3]
    awayOdd = oddRow[4]
    changeTime = oddRow[5]
    if currentId is None:
        currentId = matchId
    if matchId != currentId:
        print("Previous ID", currentId)
        currentId = matchId
        print("current ID", currentId)
    if currentId not in oddSummaryList.keys():
        oddSummaryList[currentId] = {}
    oddSummaryList[currentId][changeTime] = {
        "decimalHandicap": decimalHandicap,
        "homeOdd": homeOdd,
        "awayOdd": awayOdd
    }

fibonacciList = [5, 10, 15, 25, 40, 65, 105, 170, 275, 445, 720]
svmMatchList = {}
for matchId in oddSummaryList.keys():
    league_id = predictionMatchList[matchId]["league_id"]
    currentOddSummary = oddSummaryList[matchId]
    convertedTime = {int(v) for v in currentOddSummary.keys()}
    matchTime = predictionMatchList[matchId]["time"]
    print("matchId")
    print(matchId)
    print(currentOddSummary.keys())
    for fibonacciTime in fibonacciList:
        adjustedFibonacciTime = fibonacciTime * 60
        findTimeTarget = int(matchTime) - int(adjustedFibonacciTime)
        nearNumber = min(convertedTime, key=lambda x: abs(x - int(findTimeTarget)))
        if league_id not in svmMatchList.keys():
            svmMatchList[league_id] = {}
        if matchId not in svmMatchList[league_id].keys():
            svmMatchList[league_id][matchId] = {}

        svmMatchList[league_id][matchId][fibonacciTime] = {
            "decimalHandicap": float(currentOddSummary[str(nearNumber)]["decimalHandicap"]),
            "home_odd": float(currentOddSummary[str(nearNumber)]["homeOdd"]),
            "awayOdd": float(currentOddSummary[str(nearNumber)]["awayOdd"])
        }
print("svmMatchList")
print(json.dumps(svmMatchList))

svmTrainList = {}
svmMatchIDList = {}
for league_id, matchItem in svmMatchList.items():
    if league_id not in svmTrainList.keys():
        svmTrainList[league_id] = []
    if league_id not in svmMatchIDList.keys():
        svmMatchIDList[league_id] = []
    for match_id, match in matchItem.items():
        matchItem = []
        for number in fibonacciList:
            matchItem.append([
                match[number]["decimalHandicap"],
                match[number]["home_odd"],
                match[number]["awayOdd"],
            ])
        svmTrainList[league_id].append(matchItem)
        svmMatchIDList[league_id].append(match_id)





modelProbiList = {}
modelPredictList = {}
for league_id, matchItem in svmTrainList.items():

    print(f"predicting league: {league_id}")
    x = np.array(matchItem)
    dataset_size = len(matchItem)
    X = x.reshape(dataset_size, -1)
    # try:
    #     X_train = genfromtxt(f"../prediction/data_set/2018-2022_{league_id}_X_train.csv", delimiter=',')
    #     X_test = genfromtxt(f"../prediction/data_set/2018-2022_{league_id}_X_test.csv", delimiter=',')
    #     y_train = genfromtxt(f"../prediction/data_set/2018-2022_{league_id}_y_train.csv", delimiter=',')
    #     y_test = genfromtxt(f"../prediction/data_set/2018-2022_{league_id}_y_test.csv", delimiter=',')
    # except:
    #     print("File not found? ")
    #     continue
    absPath = "C:\\Users\\Adam\\Documents\\workspace\\python\\oddsAnalysis\\prediction\\data_set\\"
    if os.path.isfile(f"{absPath}2018-2022_{league_id}_X_train.csv") is False:
        continue
    X_train = genfromtxt(f"{absPath}2018-2022_{league_id}_X_train.csv", delimiter=',')
    X_test = genfromtxt(f"{absPath}2018-2022_{league_id}_X_test.csv", delimiter=',')
    y_train = genfromtxt(f"{absPath}2018-2022_{league_id}_y_train.csv", delimiter=',')
    y_test = genfromtxt(f"{absPath}2018-2022_{league_id}_y_test.csv", delimiter=',')
    if league_id not in modelProbiList.keys():
        modelProbiList[league_id] = {}
    if league_id not in modelPredictList.keys():
        modelPredictList[league_id] = {}
    if league_id not in asian_odd_config_classifiers.keys():
        continue
    for name, clf in asian_odd_config_classifiers[league_id].items():
        clf.fit(X_train, y_train)
        modelProbiList[league_id][name] = clf.predict_proba(X)
        modelPredictList[league_id][name] = clf.predict(X)

print(modelProbiList)
# print(modelPredictList)


for league_id, predictModel in modelProbiList.items():

    for predictModelName, predictionArray in predictModel.items():
        print(predictModelName)
        for index in range(len(svmMatchIDList[league_id])):
            print(f"index: {index}")
            match_id = svmMatchIDList[league_id][index]
            print(f"match: {match_id}")
            print("prediction?")
            print(predictionArray[index])
            predictionMatchList[match_id]["prediction"].append({
                "model_name": predictModelName,
                "probilities": predictionArray[index].tolist()
            })

print(predictionMatchList)

league_list = {}
leagues = c.getAllLeagues()
for league in leagues:
    league_list[league[0]] = {
        "eng_name": league[1],
        "tc_name": league[2],
        "sc_name": league[3],
    }

teams = c.getAllTeams()
team_list = {}
for team in teams:
    team_list[team[1]] = {
        "eng_name": team[2],
        "tc_name": team[3],
        "sc_name": team[4],
    }

for match_id, match_details in predictionMatchList.items():
    home_team = team_list[match_details['home_team']]['tc_name']
    away_team = team_list[match_details['away_team']]['tc_name']
    temp_time = match_details["time"]
    dateFormat = "%Y-%m-%d %H:%M"
    match_time = datetime.datetime.fromtimestamp(temp_time, datetime.timezone(datetime.timedelta(hours=8))).strftime(dateFormat)
    # match_time = match_details["time"]
    prediction_string = ""
    for prediction in match_details["prediction"]:
        max_probability = max(prediction["probilities"])
        max_probability_key = prediction["probilities"].index(max_probability)
        print(f"max_probability: {max_probability}")
        print(f"max_probability_key: {max_probability_key}")
        predicted_team = 0
        draw_team_probability = round(prediction['probilities'][0] * 100, 2)
        home_team_probability = round(prediction['probilities'][1] * 100, 2)
        away_team_probability = round(prediction['probilities'][2] * 100, 2)
        predicted_probability_string = f"走盤: {draw_team_probability}% 主: {home_team_probability}%, 客: {home_team_probability}%"
        if max_probability_key == 1:
            predicted_team = home_team
            predicted_probability_string = f"主: <b>{home_team_probability}</b>%, 客: {away_team_probability}%"
        if max_probability_key == 2:
            predicted_team = away_team
            predicted_probability_string = f"主: {home_team_probability}%, 客: <b>{away_team_probability}</b>%"

        string = f"\nModel: {prediction['model_name']}, \n預測: {predicted_team}, \n機會率: {predicted_probability_string} \n\n"
        prediction_string = "".join((prediction_string,string))

    message = f"{league_list[match_details['league_id']]['tc_name']} {match_time} \n {home_team} vs {away_team}\n {prediction_string}"
    print("Message")
    print(message)
    work = c.findWorkByMatchId(match_id)
    if len(work) == 0:
        continue
    if work[0][4] == 0:
        c.updateSchedule(message,4,work[0][0])


record_end_time = datetime.datetime.now()
print(f"time use: {record_end_time - record_start_time}")





