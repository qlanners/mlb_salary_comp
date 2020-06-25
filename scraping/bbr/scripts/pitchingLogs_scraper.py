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
    s = s.split('\\xa0')[0]
    return str(dt.datetime.strptime(s + ' ' + str(year), '%b %d %Y').date())

def change_doubleHeader(col):
    s = col.split('(')
    if len(s)==2:
        return s[1][0]
    else:
        return 0


def make_gameKey(col):
    if col[0] == 'h':
        s1 = str(col[1])
        s1 = s1.replace('-','')

        s2 = str(col[2])
        s3 = str(col[3])
        s4 = str(col[4])
        s= s1+s2+s3+s4
        return s

    else:
        s1 = str(col[1])
        s1 = s1.replace('-','')

        s2 = str(col[2])
        s3 = str(col[3])
        s4 = str(col[4])
        s= s1+s3+s2+s4
        return s

def change_away(col):
    if col=='@':
        return 'a'
    else:
        return 'h'

def change_decision(col):
    dec = str(col)
    dec = dec.split('(')[0]
    if dec == 'nan':
        return np.nan
    else:
        return dec

def change_entry_inning(col):
    s = col.split()[0]
    return s

def change_entry_bases(col):
    s = col.split()[1]
    return s

def change_entry_outs(col):
    s1 = col.split()[1]
    s2 = col.split()[2]

    if s1 == 'start':
        return 0
    else:
        return s2

def change_entry_score(col):
    s1 = col.split()[1]
    s = col.split()

    if s1 == 'start':
        return "".join(s[2:])
    else:
        return "".join(s[4:])

def change_exit_bases(col):
    s12 = " ".join(col.split()[1:3])
    s1 = col.split()[1]

    if s12 == '3 out':
        return 'endInning'
    elif s1 == 'end':
        return 'endGame'
    else:
        return s1

def change_exit_outs(col):
    s1 = col.split()[1]
    s2 = col.split()[2]

    if s1 == '3' or s1 == 'end':
        return 3
    else:
        return s2

def change_exit_score(col):
    s2 = col.split()[-2]
    s1 = col.split()[-1]
    s = "".join(col.split()[-2:])

    if s2 == 'out' and s1 != 'tie':
        return s1
    elif s1 == 'tie':
        return s1
    else:
        return s

##################################################################
##################################################################

#
# conn = sqlite3.connect('mlb_salary_comp_v2.db')
# cur = conn.cursor()

##################################################################
##########  Create tables in the database
##################################################################

# cur.execute(
# """
# DROP TABLE IF EXISTS pitching_gamelogs;
# """)
#
# cur.execute(
# """
#     CREATE TABLE pitching_gamelogs (
#     nameKey TEXT,
#     gameKey TEXT,
#     date TEXT,
#     doubleHeader INTEGER,
#     year INTEGER,
#     rk INTEGER,
#     gcar INTEGER,
#     gtm TEXT,
#     team TEXT,
#     homeOrAway TEXT,
#     opp TEXT,
#     result TEXT,
#     innings TEXT,
#     decision TEXT,
#     dr INTEGER,
#     ip REAL,
#     h INTEGER,
#     r INTEGER,
#     er INTEGER,
#     bb INTEGER,
#     so INTEGER,
#     hr INTEGER,
#     hbp INTEGER,
#     era REAL,
#     bf INTEGER,
#     pitches INTEGER,
#     str INTEGER,
#     strLook INTEGER,
#     strSwing INTEGER,
#     gb INTEGER,
#     fb INTEGER,
#     ld INTEGER,
#     pu INTEGER,
#     unkn INTEGER,
#     gsc INTEGER,
#     ir INTEGER,
#     inherScore INTEGER,
#     sb INTEGER,
#     cs INTEGER,
#     po INTEGER,
#     ab INTEGER,
#     double INTEGER,
#     triple INTEGER,
#     ibb INTEGER,
#     gdp INTEGER,
#     sf INTEGER,
#     roe INTEGER,
#     ali REAL,
#     wpa REAL,
#     re24 REAL,
#     inningEntry TEXT,
#     basesAtEntry TEXT,
#     outsAtEntry INTEGER,
#     scoreAtEntry TEXT,
#     inningExit TEXT,
#     basesAtExit TEXT,
#     outsAtExit INTEGER,
#     scoreAtExit TEXT
#                         );
# """)
##################################################################
##################################################################

# searchDf = pd.read_sql_query("""
# SELECT DISTINCT nameKey, year
# FROM meta
# --WHERE team = 'TOR'
# --AND year = 2018
# --ORDER BY RANDOM()
# --LIMIT 200
# ORDER BY year, nameKey
# ; """, conn)
#
# size = len(searchDf)
size=2

df = pd.DataFrame()
# logs = open("pitchingErrorLogs.txt", "w+")

counter = 0
# for nameKey,year in zip(searchDf.nameKey, searchDf.year):
for nameKey,year in zip(['porteco01','miranju01'], [2004,2010]):
    counter += 1

    try:
        url = 'https://www.baseball-reference.com/players/gl.fcgi?id=' + nameKey + '&t=p&year=' + str(year)
        res= requests.get(url)
        soup=bs4.BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table', {'id':'pitching_gamelogs'})

        dfTemp = pd.read_html(str(table), header=0, )[0]
        dfTemp = dfTemp[(dfTemp['Tm']!='Tm')]
        dfTemp = dfTemp[dfTemp['Date'].isnull() ==False]

        dfTemp['Dec'] = dfTemp['Dec'].apply(change_decision)
        dfTemp['Unnamed: 5'] = dfTemp['Unnamed: 5'].apply(change_away)
        dfTemp['DateNum'] = dfTemp['Date'].apply(change_date)
        dfTemp['doubleHeader'] = dfTemp['Date'].apply(change_doubleHeader)
        dfTemp['gameKey'] = dfTemp[['Unnamed: 5','DateNum','Tm','Opp','doubleHeader']].apply(make_gameKey, axis=1)
        dfTemp['nameKey'] = nameKey
        dfTemp['year'] = year
        dfTemp['inningEntry'] = dfTemp['Entered'].apply(change_entry_inning)
        dfTemp['basesAtEntry'] = dfTemp['Entered'].apply(change_entry_bases)
        dfTemp['outsAtEntry'] = dfTemp['Entered'].apply(change_entry_outs)
        dfTemp['scoreAtEntry'] = dfTemp['Entered'].apply(change_entry_score)

        dfTemp['inningExit'] = dfTemp['Exited'].apply(change_entry_inning)
        dfTemp['basesAtExit'] = dfTemp['Exited'].apply(change_exit_bases)
        dfTemp['outsAtExit'] = dfTemp['Exited'].apply(change_exit_outs)
        dfTemp['scoreAtExit'] = dfTemp['Exited'].apply(change_exit_score)

        dfTemp = dfTemp[['nameKey','gameKey', 'DateNum', 'doubleHeader','year',
         'Rk', 'Gcar', 'Gtm',  'Tm', 'Unnamed: 5', 'Opp', 'Rslt', 'Inngs',
       'Dec', 'DR', 'IP', 'H', 'R', 'ER', 'BB', 'SO', 'HR', 'HBP', 'ERA', 'BF',
       'Pit', 'Str', 'StL', 'StS', 'GB', 'FB', 'LD', 'PU', 'Unk', 'GSc', 'IR',
       'IS', 'SB', 'CS', 'PO', 'AB', '2B', '3B', 'IBB', 'GDP', 'SF', 'ROE',
       'aLI', 'WPA', 'RE24',
       'inningEntry', 'basesAtEntry',
       'outsAtEntry', 'scoreAtEntry', 'inningExit', 'basesAtExit',
       'outsAtExit', 'scoreAtExit']]

        dfTemp.columns= ['nameKey','gameKey', 'date', 'doubleHeader','year',
         'rk', 'gcar', 'gtm',  'team', 'homeOrAway', 'opp', 'result', 'innings',
       'decision', 'dr', 'ip', 'h', 'r', 'er', 'bb', 'so', 'hr', 'hbp', 'era', 'bf',
       'pitches', 'str', 'strLook', 'strSwing', 'gb', 'fb', 'ld', 'pu', 'unkn', 'gsc', 'ir',
       'inherScore', 'sb', 'cs', 'po', 'ab', 'double', 'triple', 'ibb', 'gdp', 'sf', 'roe',
       'ali', 'wpa', 're24',
       'inningEntry', 'basesAtEntry',
       'outsAtEntry', 'scoreAtEntry', 'inningExit', 'basesAtExit',
       'outsAtExit', 'scoreAtExit']

        df = df.append(dfTemp)

        if counter % 100 ==0:

            df.to_sql('pitching_gamelogs', con=conn, if_exists='append', index=False)
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
            # logs.write(url+ '\t' + errorDetailPosition+ '\n')
        except:
            print('error with', nameKey, 'Unknown')
            # logs.write(url+ '\t' + 'Unknown' + '\n')

# df.to_sql('pitching_gamelogs', con=conn, if_exists='append', index=False)
#df.to_csv('test.csv', index=False)


elapsed_ = perf_counter() - start
hours   = floor(elapsed_ / 60**2)
minutes = floor((elapsed_ - hours*60**2) / 60)
seconds = floor(elapsed_ - hours*60**2 -minutes*60)
print(counter, 'of', size, nameKey, year,' - ', 'Start:', startTime,' - ',  'Elapsed:',  hours, 'h', minutes, 'm', seconds, 's')

# conn.close()
# logs.close()
