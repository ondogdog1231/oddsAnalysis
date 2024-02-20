# coding=utf-8
import sys
import os
projectPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(projectPath)
sys.stdout.reconfigure(encoding='utf-8')
from config import connector
import argparse
import datetime



c = connector.config()
parser = argparse.ArgumentParser(description='New League')
parser.add_argument('leagueId', type=int, help="League ID")
args = parser.parse_args()
leagueId = args.leagueId

seasons = ["2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023"]
years = range(2018, 2023 + 1)
years_str = [str(year) for year in years]
all_seasons = seasons + years_str

current_date = datetime.datetime.now()
one_month_ago = current_date - datetime.timedelta(days=30)
adjusted_date = one_month_ago.replace(hour=23, minute=59, second=59)
unix_time = int(adjusted_date.timestamp())

# matchDetails = c.getMatchByBetweenTimeAndSeasonAndStarted(leagueId, unix_time, all_seasons)
# matchDetails = c.getMatchAllByInLeagueIdAndInSeason(leagueId, all_seasons)
matchDetails = c.getMatchAllByID(leagueId)

matchList = [item[0] for item in matchDetails]
predictionMatchList = {}


for matchDetail in matchDetails:
    try:
        if matchDetail[11] is None:
            continue
        if len(matchDetail[11].split("-")) <= 1:
            continue
        matchFinalHomeResult = matchDetail[11].split("-")[0]
        matchFinalAwayResult = matchDetail[11].split("-")[1]
        netResult = int(matchFinalHomeResult) + int(matchFinalAwayResult)
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

company_id = 3
oddsResult = c.findOverDownOddsByIdInAndCompanyId(company_id, matchList)

currentId = None
oddSummaryList = {}
for oddRow in oddsResult:
    matchId, companyId, decimalHandicap, overOdd, downOdd, changeTime = oddRow
    oddSummaryList.setdefault(matchId,{})
    oddSummaryList[matchId][changeTime] = {
        "decimalHandicap": decimalHandicap,
        "overOdd": overOdd,
        "downOdd": downOdd
    }
    predictionMatchList[currentId]["last_handicap"] = decimalHandicap
# last_item_key, last_item_value = list(oddSummaryList[1915].items())[-1]
print(predictionMatchList)
exit()
# fibonacciList = [5, 10, 15, 25, 40, 65, 105, 170, 275, 445, 720]
fibonacciList = [10, 15, 25, 40, 65, 105, 170, 275, 445, 720]
xAsisDataSet = []