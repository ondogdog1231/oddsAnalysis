import time

import os
from mysql import connector
from dotenv import load_dotenv
from contextlib2 import closing

load_dotenv()


class config:

    def __init__(self):
        self.cnx = connector.connect(
            user=os.environ.get('MYSQL_USER'),
            password=os.environ.get('MYSQL_PASSWORD'),
            host='127.0.0.1',
            database='soccer',
            charset='utf8mb4',
        )

    def getMatch(self, outsideMatchID):
        cursor = self.cnx.cursor()
        sql = """select id,outside_match_id from matches where outside_match_id  = %s;"""
        cursor.execute(sql, (outsideMatchID,))
        results = cursor.fetchone()
        return results

    def getMatchByID(self, id):
        cursor = self.cnx.cursor()
        sql = """select id,outside_match_id,date_time,season, full_time_result from matches where id = %s;"""
        cursor.execute(sql, (id,))
        results = cursor.fetchall()
        return results

    def getMatchAllFieldsByID(self, id):
        cursor = self.cnx.cursor()
        sql = """select date_time from matches where id = %s;"""
        cursor.execute(sql, (id,))
        results = cursor.fetchone()
        return results

    def getMatchWithIn(self, currentDate):
        cursor = self.cnx.cursor()
        sql = """select id,outside_match_id,date_time,season,full_time_result from matches where date_time < %s order by date_time asc;"""
        cursor.execute(sql, (currentDate,))
        results = cursor.fetchall()
        return results

    def getMatchByLeagueId(self, leagueID):
        cursor = self.cnx.cursor()
        sql = """select id,outside_match_id,date_time,season from matches where outside_league_id = %s order by date_time asc;"""
        cursor.execute(sql, (leagueID,))
        results = cursor.fetchall()
        return results

    def getMatchByLeagueIdAndSeason(self, leagueID, season):
        cursor = self.cnx.cursor()
        sql = """select id,outside_match_id,date_time,season from matches where outside_league_id = %s and season = %s order by date_time asc;"""
        cursor.execute(sql, (leagueID, season,))
        results = cursor.fetchall()
        return results

    def getMatchByLeagueIdAndInSeason(self, leagueID, season=[]):
        in_p = ', '.join(list(map(lambda x: '%s', season)))

        # sql = """select id,outside_match_id,date_time,season, full_time_result from matches where outside_league_id = %s and season in (%s) and id between 382 and 650 order by date_time asc;"""
        sql = """select id,outside_match_id,date_time,season, full_time_result from matches where outside_league_id = %s and season in (%s) order by date_time asc;"""
        # sql = sql % in_p
        sql = sql % ('%s', in_p)
        params = []
        params.append(leagueID)
        params.extend(season)
        cursor = self.cnx.cursor()
        cursor.execute(sql, tuple(params))
        results = cursor.fetchall()
        return results

    def getMatchByIdIn(self, Id=[]):
        in_p = ', '.join(list(map(lambda x: '%s', Id)))

        # sql = """select id,outside_match_id,date_time,season, full_time_result from matches where outside_league_id = %s and season in (%s) and id between 382 and 650 order by date_time asc;"""
        sql = """select id,outside_match_id,date_time,season, full_time_result from matches where id in (%s) order by date_time asc;"""
        sql = sql % in_p
        # sql = sql % ('(%s)', in_p)
        params = []
        # params.append(leagueID)
        params.extend(Id)
        cursor = self.cnx.cursor()
        cursor.execute(sql, tuple(params))
        results = cursor.fetchall()
        return results

    def getMatchDetailsAllByIdIn(self, Id=[]):
        in_p = ', '.join(list(map(lambda x: '%s', Id)))
        sql = """select * from matches where id in (%s) order by date_time asc;"""
        sql = sql % in_p
        # sql = sql % ('(%s)', in_p)
        params = []
        # params.append(leagueID)
        params.extend(Id)
        cursor = self.cnx.cursor()
        cursor.execute(sql, tuple(params))
        results = cursor.fetchall()
        return results
        return results

    def getMatchAllByInLeagueIdAndInSeason(self, outLeagueId, season=[]):
        in_p = ', '.join(list(map(lambda x: '%s', season)))

        # sql = """select id,outside_match_id,date_time,season, full_time_result from matches where outside_league_id = %s and season in (%s) and id between 382 and 650 order by date_time asc;"""
        sql = """select * from matches where outside_league_id = %s and season in (%s) order by 
        date_time asc;"""

        sql = sql % ('%s', in_p)
        params = []
        params.append(outLeagueId)
        params.extend(season)
        cursor = self.cnx.cursor()

        cursor.execute(sql, tuple(params))
        results = cursor.fetchall()
        return results

    def getMatchByInLeagueIdAndInSeason(self, season=[]):
        in_p = ', '.join(list(map(lambda x: '%s', season)))

        # sql = """select id,outside_match_id,date_time,season, full_time_result from matches where outside_league_id = %s and season in (%s) and id between 382 and 650 order by date_time asc;"""
        sql = """select id,outside_match_id,date_time,season, full_time_result from matches where outside_league_id in (8,11,31,34,36) and season in (%s) order by date_time asc;"""

        print(in_p)
        sql = sql % in_p
        # sql = sql % ('%s', in_p)
        params = []
        # params.append(leagueID)
        params.extend(season)
        cursor = self.cnx.cursor()
        cursor.execute(sql, tuple(params))
        results = cursor.fetchall()
        return results

    def getMatchByLeagueIdAndTime(self, leagueID, startTime, endTime):
        cursor = self.cnx.cursor()
        sql = """select id,outside_match_id,date_time,season,full_time_result from matches where outside_league_id = %s and date_time between %s and %s order by date_time asc;"""
        cursor.execute(sql, (leagueID, startTime, endTime,))
        results = cursor.fetchall()
        return results

    def getMatchByBetweenTime(self, startTime, endTime):
        cursor = self.cnx.cursor()
        sql = """select id,outside_match_id,date_time,season from matches where date_time between %s and %s order by date_time asc;"""
        cursor.execute(sql, (startTime, endTime,))
        results = cursor.fetchall()
        return results

    def getMatchByBetweenTime(self, startTime, endTime):
        cursor = self.cnx.cursor()
        sql = """select id,outside_match_id,date_time,season from matches where date_time between %s and %s order by date_time asc;"""
        cursor.execute(sql, (startTime, endTime,))
        results = cursor.fetchall()
        return results

    def getMatchByBetweenTimeAndSeason(self, league_id, end_time, seasons=[]):
        # Create a string of placeholders for the "IN" clause in the SQL query
        # e.g., if there are 3 seasons, create a string "%s, %s, %s"
        placeholders = ', '.join(['%s'] * len(seasons))

        # Construct the SQL query with placeholders for parameter substitution
        sql = f"""select * from matches 
                  where outside_league_id = %s and date_time <= %s and season in ({placeholders}) 
                  order by date_time asc;"""

        # Combine all parameters into a single tuple
        params = (league_id, end_time) + tuple(seasons)

        cursor = self.cnx.cursor()
        cursor.execute(sql, params)
        results = cursor.fetchall()
        return results

    def getMatchByBetweenTimeAndSeasonAndStarted(self, league_id, end_time, seasons=[]):
        # Create a string of placeholders for the "IN" clause in the SQL query
        # e.g., if there are 3 seasons, create a string "%s, %s, %s"
        placeholders = ', '.join(['%s'] * len(seasons))

        # Construct the SQL query with placeholders for parameter substitution
        sql = f"""select * from matches 
                  where outside_league_id = %s and date_time <= %s and season in ({placeholders}) and 
                  full_time_result != "推迟|推遲|Delay"
                  order by date_time asc;"""

        # Combine all parameters into a single tuple
        params = (league_id, end_time) + tuple(seasons)

        cursor = self.cnx.cursor()
        cursor.execute(sql, params)
        results = cursor.fetchall()
        return results

    def getMatchBetweenTime(self, startTime, endTime):
        cursor = self.cnx.cursor()
        sql = """select id,outside_match_id,date_time,full_time_result from matches where date_time between %s and %s;"""
        cursor.execute(sql, (startTime, endTime,))
        results = cursor.fetchall()
        return results

    def getMatchBetweenTimeAndLeagueId(self, startTime, endTime, leagueId):
        cursor = self.cnx.cursor()
        sql = """select id,outside_match_id,date_time,season,full_time_result from matches where date_time between %s and %s and outside_league_id = %s and full_time_result != '推迟|推遲|Delay';"""
        cursor.execute(sql, (startTime, endTime, leagueId,))
        results = cursor.fetchall()
        return results

    def checkOddsExist(self, matchID, companyID, decimalHandicap, changeTime, homeOdd, awayOdd):
        cursor = self.cnx.cursor()
        sql = """select id from odds where match_id = %s and company_id = %s and decimal_handicap = %s  and change_time = %s and home_odd = %s and away_odd = %s;"""
        cursor.execute(sql, (matchID, companyID, decimalHandicap, changeTime, homeOdd, awayOdd,))
        results = cursor.fetchone()
        return results

    def updateDecimalHandicap(self, matchID, decimalHandicap):
        updatedTime = int(time.time())
        sql = """UPDATE `soccer`.`odds` SET `decimal_handicap` = %s, updated_time = %s WHERE id = %s;"""
        try:
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(sql, (decimalHandicap, updatedTime, matchID,))
            self.cnx.commit()

        except TypeError as e:
            print(e.message)
            return False

    def updateMatchResultAndTime(self, matchID, home_team_id, away_team_id, halfTimeResult, fullTimeResult, raw_time,
                                 unixTime):
        updatedTime = int(time.time())
        print(f"raw_time: {raw_time}")
        sql = """UPDATE `soccer`.`matches` SET `half_time_result` = %s,`full_time_result` = %s,`home_team_id` = %s,`away_team_id` = %s, updated_time = %s, raw_date_time = %s, date_time = %s WHERE id = %s;"""
        try:
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(sql, (
                    halfTimeResult, fullTimeResult, home_team_id, away_team_id, updatedTime, raw_time, unixTime,
                    matchID,))
            self.cnx.commit()

        except TypeError as e:
            print(e.message)
            return False

    def updateMatchResult(self, matchID, halfTimeResult, fullTimeResult):
        updatedTime = int(time.time())
        sql = """UPDATE `soccer`.`matches` SET `half_time_result` = %s,`full_time_result` = %s, updated_time = %s WHERE id = %s;"""
        try:
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(sql, (halfTimeResult, fullTimeResult, updatedTime, matchID,))
            self.cnx.commit()

        except TypeError as e:
            print(e.message)
            return False

    def findWorkByMatchId(self, match_id):
        cursor = self.cnx.cursor()
        sql = """select * from `soccer`.`schedule` where match_id = %s;"""
        cursor.execute(sql, (match_id,))
        results = cursor.fetchall()
        return results

    def findWorkBeforeTimeAndStatus(self, time, status):
        cursor = self.cnx.cursor()
        sql = """select * from `soccer`.`schedule` where schedule_time <= %s and status = %s;"""
        cursor.execute(sql, (time, status))
        results = cursor.fetchall()
        return results

    def findOdds(self, ):
        cursor = self.cnx.cursor()
        sql = """select id, handicap from odds order by id asc;"""
        cursor.execute(sql)
        results = cursor.fetchall()
        return results

    def findOddsByCompanyAndAndLeagueAndHandicap(self, companyId, decimalHandicap):
        cursor = self.cnx.cursor()
        sql = """select match_id, home_odd,away_odd,change_time from odds where company_id = %s and decimal_handicap = %s and result is null order by match_id asc;"""
        cursor.execute(sql, (companyId, decimalHandicap))
        results = cursor.fetchall()
        return results

    def findOddsByCompanyAndHandicap(self, companyId, decimalHandicap):
        cursor = self.cnx.cursor()
        sql = """select match_id, home_odd,away_odd,change_time from odds where company_id = %s and decimal_handicap = %s and result is null order by match_id asc;"""
        cursor.execute(sql, (companyId, decimalHandicap))
        results = cursor.fetchall()
        return results

    def findOddsByMatchID(self, matchId):
        cursor = self.cnx.cursor()
        sql = """select match_id, company_id, decimal_handicap, change_time from odds where match_id = %s;"""
        cursor.execute(sql, (matchId,))
        results = cursor.fetchall()
        return results

    def findOddsByMatchIDAndCompanyId(self, matchId, companyId):
        cursor = self.cnx.cursor()
        sql = """select match_id, company_id, decimal_handicap, home_odd, away_odd,change_time from odds where match_id = %s and company_id = %s;"""
        cursor.execute(sql, (matchId, companyId,))
        results = cursor.fetchall()
        return results

    def findOddsByIdInAndCompanyId(self, companyId, matchId=[]):
        in_p = ', '.join(list(map(lambda x: '%s', matchId)))
        # sql = """select match_id, company_id, decimal_handicap, home_odd, away_odd, change_time from odds where company_id = %s and match_id in (%s) and match_id between 382 and 650 and result is null order by match_id asc, change_time asc;"""
        sql = """select match_id, company_id, decimal_handicap, home_odd, away_odd, change_time from odds where company_id = %s and match_id in (%s) and result is null order by match_id asc, change_time asc;"""
        sql = sql % ('%s', in_p)
        params = []
        params.append(companyId)
        params.extend(matchId)
        cursor = self.cnx.cursor()
        cursor.execute(sql, tuple(params))
        results = cursor.fetchall()
        return results

    def checkNewsExist(self, token):
        cursor = self.cnx.cursor()
        sql = """select token from news where token = %s limit 1"""
        cursor.execute(sql, (token,))
        results = cursor.fetchall()
        if results:
            return True
        else:
            return False

    def getAllHomeTeams(self):
        cursor = self.cnx.cursor()
        sql = """select distinct home_team_id from matches order by home_team_id asc;"""
        cursor.execute(sql)
        results = cursor.fetchall()
        return results

    def getAllAwayTeams(self):
        cursor = self.cnx.cursor()
        sql = """select distinct away_team_id from matches  order by away_team_id asc;"""
        cursor.execute(sql)
        results = cursor.fetchall()
        return results

    def getAllTeams(self):
        cursor = self.cnx.cursor()
        sql = """select * from teams;"""
        cursor.execute(sql)
        results = cursor.fetchall()
        return results

    def getAllFieldsInLeagues(self):
        cursor = self.cnx.cursor()
        sql = """select * from leagues;"""
        cursor.execute(sql)
        results = cursor.fetchall()
        return results

    def getAllLeagues(self):
        cursor = self.cnx.cursor()
        sql = """select outside_league_id, name,tc_name,sc_name from leagues;"""
        cursor.execute(sql)
        results = cursor.fetchall()
        return results

    def checkTeamsExist(self, outside_team_id):
        cursor = self.cnx.cursor()
        sql = """select id from teams where outside_team_id = %s limit 1"""
        cursor.execute(sql, (outside_team_id,))
        results = cursor.fetchall()
        if results:
            return True
        else:
            return False

    def checkPrediction(self, match_id, model_name):
        cursor = self.cnx.cursor()
        sql = """select * from prediction where match_id = %s and model = %s limit 1"""
        cursor.execute(sql, (match_id, model_name,))
        result = cursor.fetchall()
        if len(result) > 0:
            return result
        else:
            return False

    def checkNation(self, nation_name):
        cursor = self.cnx.cursor()
        sql = """select * from nations where chinese_name = %s limit 1"""
        cursor.execute(sql, (nation_name,))
        results = cursor.fetchall()
        if results:
            return True
        else:
            return False

    def insertNation(self, paraList):
        sql = """INSERT INTO `soccer`.`nations`
            (
            `chinese_name`)
            VALUES
            (
            %s
            );"""
        try:
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(sql, paraList)
            self.cnx.commit()
        except TypeError as e:
            print(e.message)
            return False

    def checkLeague(self, outside_league_id):
        cursor = self.cnx.cursor()
        sql = """select * from leagues where outside_league_id = %s limit 1"""
        cursor.execute(sql, (outside_league_id,))
        results = cursor.fetchall()
        if results:
            return True
        else:
            return False
    def queryPredictionIsNull(self, date_time):
        cursor = self.cnx.cursor()
        sql = """SELECT 
    p.id, m.full_time_result, net
FROM
    prediction p
        LEFT JOIN
    matches m ON p.match_id = m.id
WHERE
    net IS NULL
        AND m.date_time <= %s
ORDER BY m.date_time DESC;"""
        cursor.execute(sql, (date_time,))
        results = cursor.fetchall()
        return results


    def insertLeague(self, paraList):
        sql = """INSERT INTO `soccer`.`leagues`
                (
                `outside_league_id`,
                `year_format`,
                `tc_name`,
                `created_time`,
                `updated_time`)
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                );"""
        try:
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(sql, paraList)
            self.cnx.commit()
        except TypeError as e:
            print(e.message)
            return False

    def insertTeams(self, paraList):
        sql = """INSERT INTO `soccer`.`teams`
(
`outside_team_id`,
`english_name`,
`tc_name`,
`sc_name`,
`created_time`,
`updated_time`)
VALUES
(
%s,
%s,
%s,
%s,
%s,
%s
);"""
        try:
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(sql, paraList)
            self.cnx.commit()

        except TypeError as e:
            print(e.message)
            return False

    def findScheduleJobsByNameAndStatus(self, name):
        cursor = self.cnx.cursor()
        sql = """select id,name,status from schedule_jobs where name = %s  limit 1"""
        cursor.execute(sql, (name,))
        result = cursor.fetchone()
        return result

    def updateScheduleJobsById(self, status, id):
        updatedTime = int(time.time())
        sql = """UPDATE `soccer`.`schedule_jobs` SET `status` = %s, updated_time = %s WHERE id = %s;"""
        try:
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(sql, (status, updatedTime, id,))
            self.cnx.commit()

        except TypeError as e:
            print(e.message)
            return False

    def insertMatch(self, paraList):
        sql = """INSERT INTO `soccer`.`matches`
(
`outside_match_id`,
`season`,
`outside_league_id`,
`raw_date_time`,
`date_time`,
`half_time_result`,
`full_time_result`,
`home_team_id`,
`away_team_id`,
`created_time`,
`updated_time`)
VALUES
(
%s,
%s,
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
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(sql, paraList)
            self.cnx.commit()

        except TypeError as e:
            print(e.message)
            return False

    def insertManyOdd(self, valueList):
        sql = """INSERT INTO `soccer`.`odds`
    (
    `match_id`,
    `company_id`,
    `handicap`,
    `decimal_handicap`,
    `home_odd`,
    `away_odd`,
    `result`,
    `change_time`,
    `created_time`,
    `updated_time`)
    VALUES
    (
    %s,
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
            with closing(self.cnx.cursor()) as cursor:
                cursor.executemany(sql, valueList)
            self.cnx.commit()

        except TypeError as e:
            print(e.message)
            return False

    def insertOdd(self, paraList):
        sql = """INSERT INTO `soccer`.`odds`
    (
    `match_id`,
    `company_id`,
    `handicap`,
    `decimal_handicap`,
    `home_odd`,
    `away_odd`,
    `result`,
    `change_time`,
    `created_time`,
    `updated_time`)
    VALUES
    (
    %s,
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
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(sql, paraList)
            self.cnx.commit()

        except TypeError as e:
            print(e.message)
            return False

    def insertSchedule(self, paraList):
        sql = """INSERT INTO `soccer`.`schedule`
    (
    `schedule_time`,
    `match_id`,
    `status`,
    `created_time`,
    `updated_time`)
    VALUES
    (
    %s,
    %s,
    %s,
    %s,
    %s
    )
    """
        try:
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(sql, paraList)
            self.cnx.commit()

        except TypeError as e:
            print(e.message)
            return False

    def insertPrediction(self, paraList):
        sql = """INSERT INTO `soccer`.`prediction`
                (
                `match_id`,
                `last_handicap`,
                `model`,
                `prediction`,
                `predict_proba`,
                `net`,
                `created_time`,
                `updated_time`)
                VALUES
                (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s);
    """
        try:
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(sql, paraList)
            self.cnx.commit()

        except TypeError as e:
            print(e.message)
            return False

    def updatePredictionNet(self, id, prediction, prediction_proba, net):
        updatedTime = int(time.time())
        sql = """UPDATE `soccer`.`prediction` SET `prediction` = %s, `predict_proba` = %s, `net` = %s , 
        `updated_time` = %s WHERE (`id` = 
        %s);"""
        try:
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(sql, (prediction, prediction_proba, net, updatedTime, id,))
            self.cnx.commit()

        except TypeError as e:
            print(e.message)
            return False

    def updateSchedule(self, message, status, id):
        updatedTime = int(time.time())
        sql = """UPDATE `soccer`.`schedule` SET `message` = %s, `status` = %s, `updated_time`= %s WHERE (`id` = %s);"""
        try:
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(sql, (message, status, updatedTime, id,))
            self.cnx.commit()

        except TypeError as e:
            print(e.message)
            return False

    def updateScheduleStatus(self, status, id):
        updatedTime = int(time.time())
        sql = """UPDATE `soccer`.`schedule` SET `status` = %s, `updated_time`= %s WHERE (`id` = %s);"""
        try:
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(sql, (status, updatedTime, id,))
            self.cnx.commit()

        except TypeError as e:
            print(e.message)
            return False

    def updatePrediction(self, param_list ):
        updatedTime = int(time.time())
        sql = """UPDATE `soccer`.`prediction` SET `net` = %s WHERE (`id` = %s);
"""
        try:
            with closing(self.cnx.cursor()) as cursor:
                cursor.execute(sql, param_list)
            self.cnx.commit()
        except TypeError as e:
            print(e.message)
            return False


if __name__ == '__main__':
    print("This is main")
    config = config()
    if config.cnx:
        print("success")
    else:
        print("connect fail")
    pass
