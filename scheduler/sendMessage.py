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

c = connector.config()
BOT_API_KEY = "5786692222:AAHHmHXf4fGx1d6x855IdPNjFt_uJVYgXOU"
methods = "sendMessage"
url = f"https://api.telegram.org/bot{BOT_API_KEY}/{methods}"

chaIDList = [
    "@soccer_predictor_1999",
    "-1001559497228",
]

job = c.findScheduleJobsByNameAndStatus("tgMessage")
print(job)


if job[2] == 4:
    exit("working now")

def messageRequest(data):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    jsonParsed = json.loads(r.content)
    print(jsonParsed)
    return jsonParsed

c.updateScheduleJobsById(4, job[0])
pendingMessages = c.findWorkBeforeTimeAndStatus(int(time.time()),4)
try:
    for message in pendingMessages:
        print(message)

        for chat_id in chaIDList:
            data = {
                'chat_id': chat_id,
                'text': message[3],
                'parse_mode': "HTML"
            }
            result = messageRequest(data)

            request_count = 0
            if result["ok"] is False:
                if result["error_code"] == 429:
                    print(json.dumps(result, indent=4, ensure_ascii=False))
                    sleep_time = result["parameters"]["retry_after"]
                    print(f"sleep_time: {sleep_time}")
                    time.sleep(sleep_time+1)
                    result = messageRequest(data)

        c.updateScheduleStatus(1,message[0])

    c.updateScheduleJobsById(0, job[0])
except:
    print("sth wrong...")
    c.updateScheduleJobsById(0, job[0])




