import requests
import bs4
import pandas as pd
import numpy as np
import datetime as dt
import sqlite3
from time import perf_counter
from math import floor

start = perf_counter()
startTime = str(dt.datetime.now().strftime("%H:%M"))
print(startTime)

##################################################################
########## Define the functions
##################################################################

def change_date(col):
    s = col.split('(')[0]
    s = s.split('\xa0')[0]
    return str(dt.datetime.strptime(s + ' ' + str(year), '%b %d %Y').date())

def change_doubleHeader(col):
    s = col.split(' (')
    if len(s)==2:
        return s[1][0]
    else:
        return 0

def change_away(col):
    if col=='@':
        return 'a'
    else:
        return 'h'

def make_gameKey(col):

    s1 = str(col[1])
    s1 = s1.replace('-','')
    s2 = str(col[2])
    s3 = str(col[3])
    s4 = str(col[4])

    if col[0] == 'h':

        return s1+s2+s3+s4

    else:

        return s1+s3+s2+s4

##################################################################
##################################################################


conn = sqlite3.connect('C:\\Users\\jfran\\OneDrive\\Documents\\Baseball Database\\MLB_20002020_database.sqlite')
cur = conn.cursor()

##################################################################
##########  Create tables in the database
##################################################################

# cur.execute(
# """
# DROP TABLE IF EXISTS batting_gamelogs_test;
# """)

# cur.execute(
# """
# CREATE TABLE batting_gamelogs (
#                         nameKey TEXT,
#                         gameKey TEXT,
#                         date TEXT,
#                         doubleHeader INTEGER,
#                         year INTEGER,
#                         rk INTEGER,
#                         gcar INTEGER,
#                         gtm TEXT,
#                         team text,
#                         homeOrAway TEXT,
#                         opp TEXT,
#                         result TEXT,
#                         innings TEXT,
#                         pa INTEGER,
#                         ab INTEGER,
#                         r INTEGER,
#                         h INTEGER,
#                         double INTEGER,
#                         triple INTEGER,
#                         hr INTEGER,
#                         rbi INTEGER,
#                         bb INTEGER,
#                         ibb INTEGER,
#                         so INTEGER,
#                         hbp INTEGER,
#                         sh INTEGER,
#                         sf INTEGER,
#                         roe  INTEGER,
#                         gdp INTEGER,
#                         sb INTEGER,
#                         cs  INTEGER,
#                         ba REAL,
#                         obp REAL,
#                         slg  REAL,
#                         ops REAL,
#                         bop  REAL,
#                         ali  REAL,
#                         wpa  REAL,
#                         re24 REAL,
#                         position TEXT
#                         );
# """)
##################################################################
##################################################################

# searchDf = pd.read_sql_query("""
# SELECT DISTINCT nameKey, year
# FROM meta
# WHERE year > 2010
# --ORDER BY RANDOM()
# --LIMIT 10
# ORDER BY year, nameKey
# ; """, conn)

# size = len(searchDf)
size = 2

df = pd.DataFrame()
logs = open("battingErrorLogs.txt", "w+")

counter = 0
# for nameKey,year in zip(searchDf.nameKey, searchDf.year):
for nameKey,year in zip(['porteco01','miranju01'], [2004,2010]):
    counter += 1

    try:
        url = 'https://www.baseball-reference.com/players/gl.fcgi?id=' + nameKey + '&t=b&year=' + str(year)
        res= requests.get(url)
        soup=bs4.BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table', {'id':'batting_gamelogs'})

        dfTemp = pd.read_html(str(table), header=0, )[0]
        dfTemp = dfTemp[(dfTemp['Date']!='Date')]
        dfTemp = dfTemp[dfTemp['Date'].isnull() ==False]

        dfTemp['Unnamed: 5'] = dfTemp['Unnamed: 5'].apply(change_away)
        dfTemp['DateNum'] = dfTemp['Date'].apply(change_date)
        dfTemp['doubleHeader'] = dfTemp['Date'].apply(change_doubleHeader)
        dfTemp['gameKey'] = dfTemp[['Unnamed: 5','DateNum','Tm','Opp','doubleHeader']].apply(make_gameKey, axis=1)
        dfTemp['nameKey'] = nameKey
        dfTemp['year'] = year

        dfTemp = dfTemp[['nameKey', 'gameKey','DateNum','doubleHeader','year','Rk', 'Gcar',
                            'Gtm',  'Tm', 'Unnamed: 5', 'Opp', 'Rslt', 'Inngs',
                           'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'IBB', 'SO', 'HBP',
                           'SH', 'SF', 'ROE', 'GDP', 'SB', 'CS', 'BA', 'OBP', 'SLG', 'OPS', 'BOP',
                           'aLI', 'WPA', 'RE24', 'Pos']]

        dfTemp.columns= ['nameKey', 'gameKey','date','doubleHeader','year','rk',
                        'gcar', 'gtm',  'team', 'homeOrAway', 'opp', 'result', 'innings',
                        'pa', 'ab','r', 'h', 'double', 'triple', 'hr', 'rbi', 'bb', 'ibb', 'so', 'hbp',
                        'sh', 'sf', 'roe', 'gdp', 'sb', 'cs', 'ba', 'obp', 'slg', 'ops', 'bop',
                        'ali', 'wpa', 're24', 'position']
        df = df.append(dfTemp)

        if counter % 100 ==0:

            df.to_sql('batting_gamelogs', con=conn, if_exists='append', index=False)
            df = pd.DataFrame()

        elapsed_ = perf_counter() - start
        hours   = floor(elapsed_ / 60**2)
        minutes = floor((elapsed_ - hours*60**2) / 60)
        seconds = floor(elapsed_ - hours*60**2 -minutes*60)
        print(counter, 'of', size, nameKey, year,' - ', 'Start:', startTime,' - ',  'Elapsed:',  hours, 'h', minutes, 'm', seconds, 's')


    except:
        try:
            errorDetailPosition = soup.find('div', {'id':'meta'}).find('strong').nextSibling.strip()
            print('error with', nameKey, errorDetailPosition, url)
            logs.write(url+ '\t' + errorDetailPosition+ '\n')
        except:
            print('error with', nameKey, 'Unknown')
            logs.write(url+ '\t' + 'Unknown' + '\n')

df.to_sql('gamelogs.batting', con=conn, if_exists='append', index=False)
#df.to_csv('test.csv', index=False)
# print(df)

elapsed_ = perf_counter() - start
hours   = floor(elapsed_ / 60**2)
minutes = floor((elapsed_ - hours*60**2) / 60)
seconds = floor(elapsed_ - hours*60**2 -minutes*60)
print(counter, 'of', size, nameKey, year,' - ', 'Start:', startTime,' - ',  'Elapsed:',  hours, 'h', minutes, 'm', seconds, 's')

conn.close()
logs.close()
