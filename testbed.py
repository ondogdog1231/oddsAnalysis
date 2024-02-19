# coding=utf-8
import sys
import os

projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(projectPath)
sys.stdout.reconfigure(encoding='utf-8')
import json
from config import connector

league_model_precision_file_path = './analysis/league_model_precision.json'
with open(league_model_precision_file_path, 'r') as json_file:
    league_model_json = json.load(json_file)

c = connector.config()

for leagueId, items in league_model_json.items():
    print(leagueId)
    for item in items:
        insertParams = (
            leagueId,
            item["name"],
            item["precision"],
            item["confidence_level"],
            item["contrary"],
            item["enable"],
        )
        c.insertPredictonModel(insertParams)

