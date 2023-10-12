# coding=utf-8
import sys
import os

projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(projectPath)
sys.stdout.reconfigure(encoding='utf-8')

import datetime
import time
from config import connector

# scheduler
"""
1. select all match in coming 3 hours
2. create send time (before match 5 mins)
3. check current time > send time & status == 0 (0 pending, 1 success, 2 fail, 4 processing)

"""
c = connector.config()

print(f"start time: {datetime.datetime.now()}")

current_time = datetime.datetime.now().strftime(f"%Y-%m-%d %H:00:00")
end_time = (datetime.datetime.now() + datetime.timedelta(hours=3)).strftime("%Y-%m-%d %H:59:59")
print(f"find match in {current_time} to {end_time}")

unix_start_time = int(time.mktime(datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S").timetuple()))
unix_end_time = int(time.mktime(datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").timetuple()))

if unix_start_time > unix_end_time:
    time1 = unix_start_time
    unix_start_time = unix_end_time
    unix_end_time = time1

print(unix_start_time, unix_end_time)
matches = c.getMatchByBetweenTime(unix_start_time, unix_end_time)

if len(matches) == 0:
    exit("empty matches")

list = []
for match in matches:
    list.append(match[0])
result = c.getMatchDetailsAllByIdIn(list)
# print(result)

for match in result:
    print(match)
    match_in_worker = c.findWorkByMatchId(match[0])
    if len(match_in_worker) > 0:
        continue
    match_para_list = (
        match[7] - 10 * 60,
        match[0],
        0,
        int(time.time()),
        int(time.time())
    )
    c.insertSchedule(match_para_list)
