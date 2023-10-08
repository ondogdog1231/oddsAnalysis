import sys
import os

projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
r = sys.path.append(projectPath)
sys.stdout.reconfigure(encoding='utf-8')

import requests
import re
import json
import time
from config import connector

#
referer = f"http://zq.titan007.com/info/index_big.htm"

headers = {
    'referer': referer,
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
}
url = "http://zq.titan007.com/jsData/infoHeaderFn.js"
result = requests.get(url, headers=headers)
content = result.text.replace("var arr=new Array();", "")
regex = r"arr\[\d+\]\s\=\s"
subst = ""

result = re.sub(regex, subst, content, 0, re.MULTILINE | re.DOTALL)

content2 = result.replace(";",",")

regex = r"\,$"
result = re.sub(regex, subst, content2, 0, re.DOTALL)

regex = r"\n+"
result = re.sub(regex, subst, result, 0, re.DOTALL)
leaguesJson = json.loads(f"[{result}]")
c = connector.config()

for info in leaguesJson:
    countryName = info[1]
    print(countryName)
    leagueArray = info[4]
    for league in leagueArray:
        league_pretty = league.split(",")
        # print(league_pretty[0])
        print(league_pretty[1])
        print(f"year: {league_pretty[4]}")
        year_format = "year"
        if "-" in str(league_pretty[4]):
            year_format = "season"
        c.insertLeague((league_pretty[0], year_format,league_pretty[1],int(time.time()),int(time.time()), ))
    c.insertNation((countryName,))

exit()
