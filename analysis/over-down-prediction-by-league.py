# coding=utf-8
import math
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
import argparse

league_model_precision_file_path = './over_down_league_model_precision.json'
with open(league_model_precision_file_path, 'r') as json_file:
    league_model_json = json.load(json_file)
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

# works = c.findWorkBeforeTimeAndStatus(int(time.time()), 0)
# for work in works:
#     print(work)
#     matchList.append(work[2])
# if len(matchList) < 1:
#     print("No match")
#     exit()

parser = argparse.ArgumentParser(description='New League')
parser.add_argument('league_id', type=int, help="match ID")
parser.add_argument('start_date', type=str, help="start_date")
parser.add_argument('end_date', type=str, help="end_date")
args = parser.parse_args()

current_time = datetime.datetime.now().strftime(f"%Y-%m-%d %H:59:59")

league_id = args.league_id

start_time = datetime.datetime.now().strftime(f"{args.start_date} 00:00:00")
end_time = datetime.datetime.now().strftime(f"{args.end_date} 23:59:59")
unix_start_time = int(time.mktime(datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").timetuple()))
unix_end_time = int(time.mktime(datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").timetuple()))

print(f"league_id: {args.league_id}, startDate: {unix_start_time}, startDate: {unix_end_time}")
matchDetails = c.getMatchBetweenTimeAndLeagueId(unix_start_time, unix_end_time, league_id)

predictionMatchList = {}
# print("matchDetails")
# print(matchDetails)
matchList = [item[0] for item in matchDetails]


for matchDetail in matchDetails:
    matchDetailsSet = {
        "last_handicap": None,
        "outside_match_id": matchDetail[3],
        "result": matchDetail[11],
        "league_id": matchDetail[5],
        "time": matchDetail[7],
        "home_team": matchDetail[8],
        "away_team": matchDetail[9],
    }
    predictionMatchList[matchDetail[0]] = matchDetailsSet

company_id = 3
oddsResult = c.findOverDownOddsByIdInAndCompanyId(company_id, matchList)

currentId = None
oddSummaryList = {}
for oddRow in oddsResult:
    matchId, companyId, decimalHandicap, overOdd, downOdd, changeTime = oddRow
    oddSummaryList.setdefault(matchId,{})
    oddSummaryList[matchId][str(changeTime)] = {
        "decimalHandicap": decimalHandicap,
        "overOdd": overOdd,
        "downOdd": downOdd
    }
    predictionMatchList[matchId]["last_handicap"] = decimalHandicap

# fibonacciList = [5, 10, 15, 25, 40, 65, 105, 170, 275, 445, 720]
fibonacciList = [10, 15, 25, 40, 65, 105, 170, 275, 445, 720]
xAsisDataSet = []
"""

"""

svmMatchList = []

for matchId in oddSummaryList.keys():
    league_id = predictionMatchList[matchId]["league_id"]
    currentOddSummary = oddSummaryList[matchId]
    convertedTime = {int(v) for v in currentOddSummary.keys()}
    matchTime = predictionMatchList[matchId]["time"]
    # print(currentOddSummary.keys())
    _matchFibonacciKeyValue = {}
    for fibonacciTime in fibonacciList:
        adjustedFibonacciTime = fibonacciTime * 60
        findTimeTarget = int(matchTime) - int(adjustedFibonacciTime)
        nearNumber = str(min(convertedTime, key=lambda x: abs(x - int(findTimeTarget))))

        fibonacciTimeKey = f"minutes_before_match_{fibonacciTime}"

        _matchFibonacciKeyValue[fibonacciTimeKey] = {
            "decimalHandicap": float(currentOddSummary[nearNumber]["decimalHandicap"]),
            "over_odd": float(currentOddSummary[nearNumber]["overOdd"]),
            "down_odd": float(currentOddSummary[nearNumber]["downOdd"])
        }
    svmMatchList.append(_matchFibonacciKeyValue)

# print(f"len: {len(matchList)}")
# print(f"len: {len(predictionMatchList)}")
# print(f"len: {len(oddSummaryList.keys())}")
# print(f"len: {len(oddSummaryList.keys())}")
#
# print(matchList)
# print("")
# print(oddSummaryList.keys())
# print("Diff")
# print(matchList - oddSummaryList.keys())
# print(filtered_list)
# exit()

# print(predictionMatchList)
keys_to_remove = matchList - oddSummaryList.keys()
filtered_predictionMatchList = {k: v for k, v in predictionMatchList.items() if k not in keys_to_remove}
# print(f"len: {len(filtered_predictionMatchList)}")
# print(f"len: {len(oddSummaryList.keys())}")
# # print(filtered_predictionMatchList)
#
# for index, match_id in enumerate(filtered_predictionMatchList):
#     print(index)
#     print(filtered_predictionMatchList[match_id])
# exit()

flattened_data = []
for match in svmMatchList:
    row = {}
    for time, betting_data in match.items():
        for key, value in betting_data.items():
            row[f'{time}_{key}'] = value
    flattened_data.append(row)

df = pd.DataFrame(flattened_data)

# logisticRegressionClf = joblib.load('../predictionModels/34_LogisticRegression_model.pkl')
# randomForestClf = joblib.load('../predictionModels/34_RandomForestClassifier_model.pkl')
# GaussianNBClf = joblib.load('../predictionModels/34_DecisionTreeClassifier_model.pkl')


predictionList = {}
# todo remove

for model in league_model_json[str(league_id)]:
    predictionList[model['name']] = {
        "prediction": None,
        "predict_proba": None,
        "contrary": model["contrary"],
        "confidence_level": model["confidence_level"]
    }
    if model["enable"] is not True:
        continue
    clf = joblib.load(f"../over-down-prediction-models/{league_id}_{model['name']}_model.pkl")
    predictionList[model['name']]["prediction"] = clf.predict(df)
    predictionList[model['name']]["predict_proba"] = clf.predict_proba(df)

# exit(predictionList.keys())
# Make predictions
# logisticRegressionPredictions = logisticRegressionClf.predict(df)
# logisticRegressionProbabilities = logisticRegressionClf.predict_proba(df)
# randomForestPredictions = randomForestClf.predict(df)
# randomForestProbabilities = randomForestClf.predict_proba(df)
# GaussianNBPredictions = GaussianNBClf.predict(df)
# GaussianNBProbabilities = GaussianNBClf.predict_proba(df)

# exit([item[3] for item in matchDetails])

matchIdList = [item[3] for item in matchDetails]

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
    # print(indices)
    prediction_fit_list[modelName] = indices

common_elements = set(prediction_fit_list[list(prediction_fit_list.keys())[0]])
for model in prediction_fit_list:
    common_elements.intersection_update(prediction_fit_list[model])

# for index in common_elements:
# matchResult =
matchPredictionResult = {}
for index, match_id in enumerate(filtered_predictionMatchList):
    matchUrl = f"https://vip.titan007.com/AsianOdds_n.aspx?id={filtered_predictionMatchList[match_id]['outside_match_id']}"
    # matchPredictionResult = {}
    net_result = filtered_predictionMatchList[match_id]['result'].split("-")
    matchPredictionResult.setdefault(matchUrl,{
        "net": int(net_result[0]) + int(net_result[1]),
        "overDown": str(float(filtered_predictionMatchList[match_id]['last_handicap'])),
        "model": {}
    })
    for modelName, predictionDetails in predictionList.items():
        if predictionDetails["predict_proba"] is None:
            continue

        predict_proba = predictionDetails["predict_proba"][index][0] if predictionDetails["prediction"][index] == \
                                                                        -1 else predictionDetails[
            "predict_proba"][index][1]

        confidence_level = next(
            (item["confidence_level"] for item in league_model_json[str(league_id)] if item["name"] ==
             modelName), None)

        if predict_proba < confidence_level:
            print(f"Match: {filtered_predictionMatchList[match_id]['outside_match_id']}, model {modelName} not fit, "
                  f'prediction:{predictionDetails["prediction"][index]} predict_proba: '
                  f"{predict_proba},"
                  f"confidence_level: {confidence_level}")
            continue
        # print(f"Model: {modelName}, Contrary:{predictionDetails['contrary']}")
        # print(f'predict_proba: {predict_proba}, prediction: {predictionDetails["prediction"][index]}, predict_proba'
        #       f': {predictionDetails["predict_proba"][index]}')
        #
        # print(f"Last handicap: {filtered_predictionMatchList[match_id]['last_handicap']}")
        matchPredictionResult[matchUrl]["model"][modelName] = str(predictionDetails["prediction"][index])
        score_split = filtered_predictionMatchList[match_id]['result'].split("-")
        net = None
        if len(score_split) > 1:
            net = int(score_split[0]) - int(score_split[1])
        insertParams = (
            match_id,
            filtered_predictionMatchList[match_id]['last_handicap'],
            modelName,
            str(predictionDetails["prediction"][index]),
            predict_proba,
            net,
            int(datetime.datetime.now().timestamp()),
            int(datetime.datetime.now().timestamp())
        )
        # @Todo Update over down prediction

        # prediction_found = c.checkPrediction(match_id, modelName)
        # print("Can found?", match_id, modelName, prediction_found)

        # if prediction_found:
        #     print("found")
        #     c.updatePredictionNet(prediction_found[0][0], str(predictionDetails["prediction"][index]), predict_proba,
        #                           net)
        #     continue
        # c.insertPrediction(insertParams)

    # print()
    # print(f"matchId {matchDetails[index]}")


# Assuming 'data' is your list of dictionaries

# Filter and transform the data according to the new criteria
output_data = []


for url, details in matchPredictionResult.items():
    model_results = details["model"].values()

    # Check if there's only one model or if all models have the same result
    if len(set(model_results)) == 1:
        prediction = next(iter(model_results))  # Get the single prediction value
        output_data.append({url: {"net": details["net"], "overDown": details["overDown"], "prediction": prediction}})

# Initialize a count variable
over_true_count = 0
over_false_count = 0
down_true_count = 0
down_false_count = 0
refund = 0
refund_count = 0

win_count = 0.0
lose_count = 0.0


# Iterate through the data

for item in output_data:
    for key, value in item.items():
        # Check conditions for counting as true
        afterHandicapNet = int(value['net']) - float(float(value['overDown']))
        prediction = "Big" if int(value['prediction']) == 1 else "Small"
        # prediction = "Small"
        # if int(value['prediction']) == -1:
        #     prediction = "Big"
        # elif int(value['prediction']) == 1:
        #     prediction = "Big"

        # print(f"key: {key} ,net :{int(value['net']) }, overDown: "
        #       f"{float(float(value['overDown']))},"
        #       f"afterHandicapNet:{afterHandicapNet},prediction: {prediction} ")
        if prediction == "Big" and afterHandicapNet > 0.0:
            win_count += 0.5 if afterHandicapNet == 0.25 else 1
            refund += 0.5 if afterHandicapNet == 0.25 else 0
        elif prediction == "Small" and afterHandicapNet < 0.0:
            # print(f'in small: {afterHandicapNet - math.floor(afterHandicapNet)}')
            win_count += 0.5 if afterHandicapNet == -0.25 else 1
            refund += 0.5 if afterHandicapNet == -0.25 else 0
        elif prediction == "Small" and afterHandicapNet > 0.0:
            lose_count += 0.5 if afterHandicapNet == 0.25 else 1
            refund += 0.5 if afterHandicapNet == 0.25 else 0
        elif prediction == "Big" and afterHandicapNet < 0.0:
            lose_count += 0.5 if afterHandicapNet == -0.25 else 1
            refund += 0.5 if afterHandicapNet == -0.25 else 0
        else:
            refund += 1
            # lose_count += 0.5 if afterHandicapNet - math.floor(afterHandicapNet) == 0.25 else 1

        # if int(value['prediction']) == 1 and int(value['net']) > float(float(value['overDown'])):
        #     over_true_count += 1
        # elif int(value['prediction']) == -1 and int(value['net']) < float(float(value['overDown'])):
        #     down_true_count += 1
        # elif int(value['prediction']) == 1 and int(value['net']) < float(value['overDown']):
        #     over_false_count += 1
        # elif int(value['prediction']) == -1 and int(value['net']) > float(value['overDown']):
        #     down_false_count += 1
        # else:
        #     refund_count += 1
        #     print("refund")

        if prediction == "Big" and afterHandicapNet > 0.0:
            over_true_count += 1
        elif prediction == "Small" and afterHandicapNet < 0.0:
            down_true_count += 1
        elif prediction == "Big" and afterHandicapNet < 0.0:
            over_false_count += 1
        elif prediction == "Small" and afterHandicapNet > 0.0:
            down_false_count += 1
        else:
            refund_count += 1
            print("refund")


print(f'over_true_count: {over_true_count}')
print(f'down_true_count: {down_true_count}')
print(f'over_false_count: {over_false_count}')
print(f'down_false_count: {down_false_count}')
print(f'refund_count: {refund_count}')

print(f"win: {win_count}")
print(f"lose: {lose_count}")
print(f"refund: {refund}")


