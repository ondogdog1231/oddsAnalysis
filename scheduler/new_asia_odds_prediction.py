# coding=utf-8
import sys
import os

projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
script_dir = os.path.dirname(os.path.realpath(__file__))

os.chdir(script_dir)

sys.path.append(projectPath)
sys.stdout.reconfigure(encoding='utf-8')

import requests
# from datetime import datetime
import datetime
import re
import json
from config import connector
from config import asianOddsConfig
import numpy as np
from numpy import genfromtxt

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import time

league_model_precision_file_path = '../analysis/league_model_precision.json'
with open(league_model_precision_file_path, 'r') as json_file:
    league_model_json = json.load(json_file)

record_start_time = datetime.datetime.now()

print(f"start time: {record_start_time}")
print(f"start time: {record_start_time.timestamp()}")

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

works = c.findWorkBeforeTimeAndStatus(int(time.time()), 0)

for work in works:
    print(work)
    matchList.append(work[2])
if len(matchList) < 1:
    print("No match")
    exit()
# matchList = [item[2] for item in matchList]
# matchList = range(21661, 21911)
# matchList = [4553, 4554]
# matchDetails = c.getMatchDetailsAllByIdIn(matchList)
matchDetails = c.getMatchDetailsAllByIdIn(matchList)
match_outside_id_list = {}
for match in matchDetails:
    match_outside_id_list[str(match[0])] = match[3]

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

predictionMatchList = {}
# print("matchDetails")
# print(matchDetails)
matchList = [item[0] for item in matchDetails]

for matchDetail in matchDetails:
    matchDetailsSet = {
        "last_handicap": None,
        "outside_match_id": matchDetail[3],
        "league_id": matchDetail[5],
        "time": matchDetail[7],
        "home_team": matchDetail[8],
        "away_team": matchDetail[9],
    }
    predictionMatchList[matchDetail[0]] = matchDetailsSet

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
        # print("Previous ID", currentId)
        currentId = matchId
        # print("current ID", currentId)
    if currentId not in oddSummaryList.keys():
        oddSummaryList[currentId] = {}
    oddSummaryList[currentId][changeTime] = {
        "decimalHandicap": decimalHandicap,
        "homeOdd": homeOdd,
        "awayOdd": awayOdd
    }
    predictionMatchList[currentId]['last_handicap'] = decimalHandicap
# last_item_key, last_item_value = list(oddSummaryList[1915].items())[-1]

# fibonacciList = [5, 10, 15, 25, 40, 65, 105, 170, 275, 445, 720]
fibonacciList = [10, 15, 25, 40, 65, 105, 170, 275, 445, 720]
xAsisDataSet = []
"""


"""
print("oddSummaryList.keys()")
print(oddSummaryList.keys())
svmTrainList = {}
svmMatchIDList = {}
svmMatchList = []
for matchId in oddSummaryList.keys():
    league_id = predictionMatchList[matchId]["league_id"]
    currentOddSummary = oddSummaryList[matchId]
    convertedTime = {int(v) for v in currentOddSummary.keys()}
    matchTime = predictionMatchList[matchId]["time"]
    if league_id not in svmTrainList.keys():
        svmTrainList[league_id] = []
    if league_id not in svmMatchIDList.keys():
        svmMatchIDList[league_id] = []
    # print(currentOddSummary.keys())
    _matchFibonacciKeyValue = {}
    for fibonacciTime in fibonacciList:
        adjustedFibonacciTime = fibonacciTime * 60
        findTimeTarget = int(matchTime) - int(adjustedFibonacciTime)
        nearNumber = min(convertedTime, key=lambda x: abs(x - int(findTimeTarget)))

        fibonacciTimeKey = f"minutes_before_match_{fibonacciTime}"

        _matchFibonacciKeyValue[fibonacciTimeKey] = {
            "decimalHandicap": float(currentOddSummary[str(nearNumber)]["decimalHandicap"]),
            "home_odd": float(currentOddSummary[str(nearNumber)]["homeOdd"]),
            "away_odd": float(currentOddSummary[str(nearNumber)]["awayOdd"])
        }
        # svmMatchList.append(_matchFibonacciKeyValue)
    svmTrainList[league_id].append(_matchFibonacciKeyValue)
    svmMatchIDList[league_id].append(matchId)
print("svmMatchIDList")
print(svmTrainList)
print("matchList")
print(matchList)
exit()
# print(svmMatchIDList[21])
for league_id in svmTrainList.keys():
    print(league_id)
    continue
    print(matchList)
    print(svmMatchIDList[league_id])
    keys_to_remove = list(set(matchList) - set(svmMatchIDList[league_id]))

    filtered_predictionMatchList = {k: v for k, v in predictionMatchList.items() if k not in keys_to_remove}
    print(f"filtered_predictionMatchList: {filtered_predictionMatchList}")

    flattened_data = []
    for svmTrainListItem in svmTrainList[league_id]:
        row = {}
        for time, betting_data in svmTrainListItem.items():
            for key, value in betting_data.items():
                row[f'{time}_{key}'] = value
        flattened_data.append(row)
    print(f"leagueId:{league_id} len: {len(flattened_data)}")
    if league_id == 39:
        print("In 34")
        print(flattened_data)
        print(flattened_data[1])
        exit()
    if len(flattened_data) < 1:
        print(f"leagueID: {league_id} has 0 data")
        continue
    df = pd.DataFrame(flattened_data)
    predictionList = {}
    if (str(league_id) in league_model_json) is False:
        print(f"{str(league_id)} not in json")
        continue
    print(f"Now processing leagueId: {league_id}")
    for model in league_model_json[str(league_id)]:
        predictionList[model['name']] = {
            "prediction": None,
            "predict_proba": None,
            "contrary": model["contrary"],
            "confidence_level": model["confidence_level"]
        }
        if model["enable"] is not True:
            continue
        # if league_id == 34:
        #     print("df")
        #     print(df)
        #     exit()
        clf = joblib.load(f"../predictionModels/{league_id}_{model['name']}_model.pkl")
        predictionList[model['name']]["prediction"] = clf.predict(df)
        predictionList[model['name']]["predict_proba"] = clf.predict_proba(df)
    # exit(predictionList)
    matchIdList = svmMatchIDList[league_id]
    prediction_fit_list = {}

    for modelName, predictionDetails in predictionList.items():
        if predictionDetails["predict_proba"] is None:
            continue
        indices = [index for index, sublist in enumerate(predictionDetails["predict_proba"]) if any(x >=
                                                                                                    predictionDetails[
                                                                                                        "confidence_level"]
                                                                                                    for x in
                                                                                                    sublist)]
        # print("indices")
        # print(f"LeagueID: {league_id}")
        # print(indices)
        # exit()
        prediction_fit_list[modelName] = indices
    common_elements = set(prediction_fit_list[list(prediction_fit_list.keys())[0]])
    for model in prediction_fit_list:
        common_elements.intersection_update(prediction_fit_list[model])
    for index, match_id in enumerate(filtered_predictionMatchList):
        print()
        print(f"filtered_predictionMatchList: {filtered_predictionMatchList}")
        match_url = f"https://vip.titan007.com/AsianOdds_n.aspx?id={filtered_predictionMatchList[match_id]['outside_match_id']}"
        print(match_url)
        messageArr = [f"{match_url} \n {league_list[league_id]['tc_name']} -" \
                      f" {team_list[filtered_predictionMatchList[match_id]['home_team']]['tc_name']} vs " \
                      f"{team_list[filtered_predictionMatchList[match_id]['away_team']]['tc_name']} \n"]
        prediction_model_success_count = 0
        for modelName, predictionDetails in predictionList.items():
            print(f"IN predictionList, league_id: {league_id}")
            # print("predictionDetails['prediction']")
            # print(predictionDetails['prediction'])
            # print(f"filtered_predictionMatchList: {filtered_predictionMatchList}")
            # print(f"match_id:{match_id}")

            if predictionDetails["predict_proba"] is None:
                continue
            print(f"Model: {modelName}, Contrary:{predictionDetails['contrary']}")
            print(f"prediction: {predictionDetails['prediction'][index]}")
            print(f"Proba: {predictionDetails['predict_proba'][index]}")
            predict_proba = predictionDetails["predict_proba"][index][0] if predictionDetails["prediction"][index] == \
                                                                            -1 else predictionDetails[
                "predict_proba"][index][1]
            print(f"predict_proba: {predict_proba}")
            print(f"league_id: {league_id}")
            print(f"Index: {index}")
            if predict_proba < predictionDetails["confidence_level"]:
                print("lower than confidence_level")
            else:
                net = None
                insertParams = (
                    match_id,
                    filtered_predictionMatchList[match_id]["last_handicap"],
                    modelName,
                    str(predictionDetails["prediction"][index]),
                    predict_proba,
                    net,
                    int(datetime.datetime.now().timestamp()),
                    int(datetime.datetime.now().timestamp())
                )
                prediction_string = "Away" if str(predictionDetails['prediction'][index]) == "-1" else "Home"
                messageArr.append(
                    f"Model: {modelName}, Prediction:" \
                    f" {prediction_string}, " \
                    f"probability: {predict_proba} \n"
                )

                # print(f"svmMatchIDList[league_id]: {svmMatchIDList[league_id]}")
                # print(matchIdList[index])
                print(f"c.checkPrediction(match_id, modelName): {c.checkPrediction(match_id, modelName)}")
                if c.checkPrediction(match_id, modelName) is False:
                    print("already have record in prediction")
                    c.insertPrediction(insertParams)
                else:
                    c.updatePredictionNet(match_id, str(predictionDetails["prediction"][index]), predict_proba, net)
                prediction_model_success_count += 1
        if prediction_model_success_count > 0:
            work = c.findWorkByMatchId(match_id)
            if len(work) == 0:
                continue
            if work[0][4] == 0:
                print(f"in work: {work[0][0]}, {' '.join(messageArr)}")
                c.updateSchedule(' '.join(messageArr), 4, work[0][0])

        svmMatchIDList[league_id].remove(match_id)
    for matchId in filtered_predictionMatchList.keys():
        work = c.findWorkByMatchId(matchId)
        if len(work) == 0:
            continue
        if work[0][4] == 0:
            c.updateSchedule(None, 2, work[0][0])
        print(f"match delete to update status 2: {matchId}")
