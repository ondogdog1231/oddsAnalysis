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
import argparse
import numpy as np
from numpy import genfromtxt

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score, recall_score, f1_score
import joblib
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

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
parser.add_argument('leagueId', type=int, help="League ID")
args = parser.parse_args()

leagueId = args.leagueId

# seasons = ["2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023"]
seasons = ["2017-2018", "2018-2019", "2019-2020", "2020-2021", "2021-2022","2022-2023"]
years = range(2017, 2021 + 1)
years_str = [str(year) for year in years]
all_seasons = seasons + years_str

# seasons = range(2018, 2022 + 1)
matchDetails = c.getMatchAllByInLeagueIdAndInSeason(leagueId, all_seasons)

# exit(matchDetails)
predictionMatchList = {}
# print("matchDetails")
# print(matchDetails)
matchList = [item[0] for item in matchDetails]

for matchDetail in matchDetails:
    try:
        if matchDetail[11] is None:
            continue
        if len(matchDetail[11].split("-")) <= 1:
            continue
        matchFinalHomeResult = matchDetail[11].split("-")[0]
        matchFinalAwayResult = matchDetail[11].split("-")[1]
        netResult = int(matchFinalHomeResult) - int(matchFinalAwayResult)
        matchDetailsSet = {
            "last_handicap": None,
            "league_id": matchDetail[5],
            "time": matchDetail[7],
            "home_team": matchDetail[8],
            "away_team": matchDetail[9],
            "net_result": netResult,
            "net_result_label": None
        }
        predictionMatchList[matchDetail[0]] = matchDetailsSet
    except Exception as e:
        print("matchDetail error")
        print(matchDetail)
        print(e)
        exit()

company_id = 1
oddsResult = c.findOddsByIdInAndCompanyId(company_id, list(predictionMatchList.keys()))

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
    predictionMatchList[currentId]["last_handicap"] = decimalHandicap
# last_item_key, last_item_value = list(oddSummaryList[1915].items())[-1]

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
    # print("matchId")
    # print(matchId)
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
    svmMatchList.append(_matchFibonacciKeyValue)
# print("svmMatchList")
# exit(json.dumps(svmMatchList))
# print(predictionMatchList)
# Calculate Net result is bigger than decimal handicap
match_to_delete = []
max_error = 0
for matchId, matchItem in predictionMatchList.items():
    try:
        if matchItem["last_handicap"] is None:
            match_to_delete.append(matchId)
            continue
        if max_error >= 10:
            exit(f"Please check last ID: {matchId}")
        net = matchItem["net_result"] + matchItem["last_handicap"]
        predictionMatchList[matchId]["net_result_label"] = -1 if net == 0 else 1 if net > 0 else -1
    except Exception as e:
        print("In error")
        print(e)
        print(matchId, matchItem)
        exit("In error")

for matchId in match_to_delete:
    del predictionMatchList[matchId]

net_result_label_dict = [value['net_result_label'] for key, value in predictionMatchList.items()]
print("net_result_label_dict")

flattened_data = []
for match in svmMatchList:
    row = {}
    for time, betting_data in match.items():
        for key, value in betting_data.items():
            row[f'{time}_{key}'] = value
    flattened_data.append(row)

df = pd.DataFrame(flattened_data)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df, net_result_label_dict, test_size=0.2, random_state=42)

model_list = {
    "LogisticRegression": LogisticRegression(max_iter=1000),
    # "DecisionTreeClassifier": DecisionTreeClassifier(random_state=42),
    "RandomForestClassifier": RandomForestClassifier(random_state=42),
    # "SVC": SVC(kernel='linear', random_state=42, probability=True)
    # "Gaussian": GaussianNB()
}
model_confidence_list = {
    "LogisticRegression": 0.55,
    # "DecisionTreeClassifier": DecisionTreeClassifier(random_state=42),
    "RandomForestClassifier": 0.6,
    # "SVC": SVC(kernel='linear', random_state=42, probability=True)
    # "Gaussian": GaussianNB()
}
for model_name, clf in model_list.items():
    print(model_name)
    clf.fit(X_train, y_train)
    joblib.dump(clf, f"../oldMatchPredictionModels/{leagueId}_{model_name}_model.pkl")
    # Evaluate the model
    y_pred = clf.predict(X_test)
    # Obtain probability estimates
    y_prob = clf.predict_proba(X_test)

    high_prob_index = np.where(np.max(y_prob, axis=1) >= model_confidence_list[model_name])[0]
    high_prob_preds = y_pred[high_prob_index]
    actual_values = np.array(y_test)[high_prob_index]
    # # Check if the predictions are correct
    correct_preds = high_prob_preds == actual_values
    # Display results
    print(f"Total samples with >55% probability: {len(high_prob_index)}")
    print(f"Correct predictions among high-probability samples: {np.sum(correct_preds)}")
    print(f"Accuracy among high-probability samples: {np.mean(correct_preds) * 100:.2f}%")
    print("")

    # Convert probabilities to a DataFrame for easier viewing
    prob_df = pd.DataFrame(y_prob,
                           columns=[f'Probability_of_class_{class_label}' for class_label in clf.classes_])

    # If you want to attach these probabilities back to your original data:
    results_df = pd.concat([X_test.reset_index(drop=True), prob_df], axis=1)

    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.max_columns', None)
    # print(prob_df)

    precision = precision_score(y_test, y_pred, average='weighted', zero_division=1)
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')

    print(f'Precision: {precision * 100:.2f}%')
    print(f'Recall: {recall * 100:.2f}%')
    print(f'F1 Score: {f1 * 100:.2f}%')
    print("")
