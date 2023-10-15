# coding=utf-8
import sys
import os

projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
script_dir = os.path.dirname(os.path.realpath(__file__))

os.chdir(script_dir)

sys.path.append(projectPath)
sys.stdout.reconfigure(encoding='utf-8')
from config import connector
from config import asianOddsConfig
import time
import datetime
c = connector.config()

after_match_time = (datetime.datetime.now() - datetime.timedelta(hours=3)).strftime("%Y-%m-%d %H:59:59")
unix_end_time = int(time.mktime(datetime.datetime.strptime(after_match_time, "%Y-%m-%d %H:%M:%S").timetuple()))

prediction_null_result = c.queryPredictionIsNull(unix_end_time)

for item in prediction_null_result:
    score_split = item[1].split("-")

    if len(score_split) != 2:
        continue
    net = int(score_split[0]) - int(score_split[1])
    param_list = (
        net,
        item[0]
    )
    print(param_list)
    c.updatePrediction(param_list)




