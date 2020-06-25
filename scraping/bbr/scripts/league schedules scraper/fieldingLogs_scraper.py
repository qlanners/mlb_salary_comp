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


conn = sqlite3.connect('mlb_salary_comp_v2.db')
cur = conn.cursor()

##################################################################
##########  Create tables in the database
##################################################################

# cur.execute(
# """
# DROP TABLE IF EXISTS fielding_gamelogs;
# """)
#
# cur.execute(
# """
# CREATE TABLE fielding_gamelogs (
#                         nameKey TEXT,
#                         gameKey TEXT,
#                         date TEXT,
#                         doubleHeader INTEGER,
#                         year INTEGER,
#                         rk INTEGER,
#                         gtm TEXT,
#                         team TEXT,
#                         homeOrAway TEXT,
#                         opp TEXT,
#                         result TEXT,
#                         innings TEXT,
#                         bf INTEGER,
#                         inn REAL,
#                         po INTEGER,
#                         a INTEGER,
#                         e INTEGER,
#                         ch INTEGER,
#                         dp INTEGER,
#                         position TEXT
#                         );
# """)
##################################################################
##################################################################

searchDf = pd.read_sql_query("""
SELECT DISTINCT nameKey, year
FROM meta
WHERE year > 2010
--ORDER BY RANDOM()
--LIMIT 10
ORDER BY year, nameKey
; """, conn)

size = len(searchDf)


df = pd.DataFrame()
logs = open("fieldingErrorLogs.txt", "w+")

counter = 0
for nameKey,year in zip(searchDf.nameKey, searchDf.year):

    counter += 1

    try:
        url = 'https://www.baseball-reference.com/players/gl.fcgi?id=' + nameKey + '&t=f&year=' + str(year)
        res= requests.get(url)
        soup=bs4.BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table', {'id':'_0'})

        dfTemp = pd.read_html(str(table), header=0, )[0]
        dfTemp = dfTemp[(dfTemp['Tm']!='Tm')]
        dfTemp = dfTemp[dfTemp['Date'].isnull() ==False]

        dfTemp['Unnamed: 4'] = dfTemp['Unnamed: 4'].apply(change_away)
        dfTemp['DateNum'] = dfTemp['Date'].apply(change_date)
        dfTemp['doubleHeader'] = dfTemp['Date'].apply(change_doubleHeader)
        dfTemp['gameKey'] = dfTemp[['Unnamed: 4','DateNum','Tm','Opp','doubleHeader']].apply(make_gameKey, axis=1)
        dfTemp['nameKey'] = nameKey
        dfTemp['year'] = year

        dfTemp = dfTemp[['nameKey','gameKey', 'DateNum', 'doubleHeader',
       'year', 'Rk', 'Gtm',  'Tm', 'Unnamed: 4', 'Opp', 'Rslt', 'Inngs', 'BF',
       'Inn', 'PO', 'A', 'E', 'Ch', 'DP', 'Pos']]

        dfTemp.columns= ['nameKey','gameKey', 'date', 'doubleHeader',
       'year', 'rk', 'gtm',  'team', 'homeOrAway', 'opp', 'result', 'innings', 'bf',
       'inn', 'po', 'a', 'e', 'ch', 'dp', 'position']
        df = df.append(dfTemp)

        if counter % 100 ==0:

            df.to_sql('fielding_gamelogs', con=conn, if_exists='append', index=False)
            df = pd.DataFrame()

        elapsed_ = perf_counter() - start
        hours   = floor(elapsed_ / 60**2)
        minutes = floor((elapsed_ - hours*60**2) / 60)
        seconds = floor(elapsed_ - hours*60**2 -minutes*60)
        print(counter, 'of', size, nameKey, year,' - ', 'Start:', startTime,' - ',  'Elapsed:',  hours, 'h', minutes, 'm', seconds, 's')


    except:
        try:
            errorDetailPosition = soup.find('div', {'id':'meta'}).find('strong').nextSibling.strip()
            print('error with', nameKey, errorDetailPosition)
            logs.write(url+ '\t' + errorDetailPosition+ '\n')
        except:
            print('error with', nameKey, 'Unknown')
            logs.write(url+ '\t' + 'Unknown' + '\n')

df.to_sql('fielding_gamelogs', con=conn, if_exists='append', index=False)
#df.to_csv('test.csv', index=False)


elapsed_ = perf_counter() - start
hours   = floor(elapsed_ / 60**2)
minutes = floor((elapsed_ - hours*60**2) / 60)
seconds = floor(elapsed_ - hours*60**2 -minutes*60)
print(counter, 'of', size, nameKey, year,' - ', 'Start:', startTime,' - ',  'Elapsed:',  hours, 'h', minutes, 'm', seconds, 's')

conn.close()
logs.close()
