# coding=utf-8
import sys
import os

projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(projectPath)
sys.stdout.reconfigure(encoding='utf-8')
from mysql import connector

import requests
import datetime
import re
import time
from config import connector
import utils.handicap as h
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib2 import closing


parser = argparse.ArgumentParser(description='Asian Odds')
parser.add_argument('leagueId', type=int, help="League ID")
parser.add_argument('start_year', type=int, help="start_year")
parser.add_argument('end_year', type=int, help="end_year")
args = parser.parse_args()

c = connector.config()
league_id = args.leagueId
start_year = args.start_year
end_year = args.end_year

years = list(range(start_year, end_year+1))
year_ranges = [f"{y}-{y+1}" for y in years[:-1]]
all_years = [str(y) for y in years]
seasons = year_ranges + all_years
matchResult = c.getMatchByLeagueIdAndInSeason(league_id,seasons)
# matchResult = c.getMatchByLeagueIdAndInSeason(league_id,["2023-2024"])
# matchResult = c.getMatchByID(58624)

headers = {
    'referer': "http://live.titan007.com/indexall_big.aspx",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
}

matchUrls = {}

for match in matchResult:
    outsideMatchId = match[1]
    matchUrl = f"http://vip.titan007.com/changeDetail/overunder.aspx?id={outsideMatchId}&companyID=3&l=1"
    datetime_utc = datetime.datetime.utcfromtimestamp(match[2])
    datetime_hkt = datetime_utc + datetime.timedelta(hours=8)
    matchYear = datetime_hkt.year
    matchMonth = datetime_hkt.month
    season = match[3].split("-")
    previousOddList = []
    previousOddResult = c.findOverDownOddsByMatchID(match[0])
    previousOddList = [f"{x[0]}_{x[1]}_{str(x[2]).replace('.', '')}_{x[3]}" for x in previousOddResult]
    matchUrls.setdefault(matchUrl, {
        'id': match[0],
        'kick_off_time': match[2],
        'match_year': matchYear,
        'season': season,
        'previousOddList': previousOddList
    })
delay_between_requests = 5

def fetch_odds(url, delay):
    # print(f'url: {url}')
    # print(f'matchID: {matchUrls[url]["id"]}')

    result = requests.get(url, headers=headers)
    oddsRegex = r"<TR align=center .*?>(.*?)<\/tr>"
    oddsPattern = re.compile(oddsRegex, re.MULTILINE | re.IGNORECASE | re.DOTALL | re.S)
    oddsResult = oddsPattern.findall(result.text)
    if len(oddsResult) < 1:
        print("odds content is null")
        return
    oddsResult = oddsResult[1:]
    rowResult = []
    for i in oddsResult:
        rowResult.append(i)
    dataForSaveToDb = []
    for i in rowResult:
        pattern = r'<td.*?>(.*?)<\/td>.*?<td.*?>(.*?)<\/td>.*?<td.*?>.*?<b>(.*?)<\/b>.*?<td.*?font.*?>(.*?)<\/td>.*?<b>(.*?)<\/b>.*?<td.*?>(.*?)<\/td>'
    # Use re.findall() to find all matches
        matches = re.findall(pattern, i, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        # print(f"matches: {matches}")
        if len(matches) < 1:
            continue
        dataResult = matches[0]
        # if len(dataResult[1]) > 0:
        #     continue
        dateResult = re.split('\s', dataResult[5])
        oddsUpdateTime = f"{matchUrls[url]['match_year']}-{dateResult[0]} {dateResult[1]}"
        unixOddUpdateDateTime = int(
            time.mktime(datetime.datetime.strptime(oddsUpdateTime, "%Y-%m-%d %H:%M").timetuple()))

        print(f"oddsUpdateTime {oddsUpdateTime}")
        print(f"unixOddUpdateDateTime:{unixOddUpdateDateTime}  matchUrls[url]['kick_off_time']:"
              f"{matchUrls[url]['kick_off_time']}")

        datetime_utc = datetime.datetime.utcfromtimestamp(unixOddUpdateDateTime)
        datetime_hkt = datetime_utc + datetime.timedelta(hours=8)
        formatted_date_hkt = datetime_hkt.strftime("%Y-%m-%d %H:%M:%S HKT")
        # print(f"Before any action: {formatted_date_hkt}")
        # print(f"{unixOddUpdateDateTime}, {matchUrls[url]['kick_off_time']}")
        # print(f"unixOddUpdateDateTime > matchUrls[url]['kick_off_time'] :{unixOddUpdateDateTime > matchUrls[url]['kick_off_time']}")
        if unixOddUpdateDateTime > matchUrls[url]['kick_off_time'] and len(dataResult[1]) == 0:
            newMatchYear = matchUrls[url]['season'][0]
            # print(f"newMatchYear {newMatchYear}")
            oddUpdateDateTime = f"{newMatchYear}-{dateResult[0]} {dateResult[1]}"
            # print(f"oddUpdateDateTime {oddUpdateDateTime}")
            unixOddUpdateDateTime = int(
                time.mktime(datetime.datetime.strptime(oddUpdateDateTime, "%Y-%m-%d %H:%M").timetuple()))
        datetime_utc = datetime.datetime.utcfromtimestamp(unixOddUpdateDateTime)
        datetime_hkt = datetime_utc + datetime.timedelta(hours=8)
        formatted_date_hkt = datetime_hkt.strftime("%Y-%m-%d %H:%M:%S HKT")
        print(f'handicap spilt result: {str(dataResult[3]).split("/")}')
        handicapSpilt = str(dataResult[3]).split("/")
        if len(handicapSpilt)> 1:
            handicapSpilt = (float(handicapSpilt[0]) + float(handicapSpilt[1]))/2
        else:
            handicapSpilt = float(handicapSpilt[0])
        companyId = 3
        oddKey = f"{matchUrls[url]['id']}_{companyId}_{str('%.2f' % handicapSpilt).replace('.', '')}_{unixOddUpdateDateTime}"
        # print(oddKey)
        # print(previousOddList)
        result = None if len(dataResult[1]) < 1 else dataResult[1]
        if oddKey in matchUrls[url]['previousOddList']:
            print("already have record")
            continue
        rowData = (
            matchUrls[url]['id'],
            companyId,
            handicapSpilt,  # handicap
            dataResult[2],  # over odds
            dataResult[4],  # down odds
            result,  # match result
            unixOddUpdateDateTime,
            int(time.time()),
            int(time.time())
        )
        dataForSaveToDb.append(rowData)
    # Save to DB
    # print(f'Url: {url}')
    cnx = connector.connection_init()
    sql = """
            INSERT INTO `soccer`.`over_down_odds` (
            `match_id`, 
            `company_id`, 
            `decimal_handicap`, 
            `over_odd`, 
            `down_odd`, 
            `result`,
            `change_time`,
            `created_time`,
            `updated_time`) VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """
    try:
        with closing(cnx.cursor()) as cursor:
            cursor.executemany(sql, dataForSaveToDb)
            cnx.commit()
    except TypeError as e:
        print(e.message)
        return False
    # c.insertOverDownManyOdd(dataForSaveToDb)
    time.sleep(delay)

def process_urls(matchUrls):
    with ThreadPoolExecutor(max_workers=20) as executor:
        urls = matchUrls.keys()
        # Create a future to URL mapping
        future_to_url = {
            executor.submit(fetch_odds, url, delay_between_requests): url for index, url in
            enumerate(urls)
        }

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print(f'{url} generated an exception: {exc}')


process_urls(matchUrls)
