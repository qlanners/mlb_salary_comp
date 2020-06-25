import requests
import bs4
import pandas as pd
from datetime import datetime
import time
from math import floor
import sqlite3
import numpy as np

'''
The objective of this scraper is
to grab, all game schedules for all seasons
'''
start = time.perf_counter()


def change_num_pitch(col):
    try:
        s = col.split(',')[0]
    except:
        s = np.nan
    return s

def change_pit_balls(col):
    try:
        s1 = col.split('-')[0]
        s= s1.split('(')[1]
    except:
        s = np.nan
    return s

def change_pit_strikes(col):
    try:
        s1 = col.split('-')[1]
        s= s1.split(')')[0]
    except:
        s = np.nan
    return s


def get_nameKey(col):
    name = col.replace('\xa0',' ')
    return nameDict[name]

def get_score_batting(col):
    s = col.split('-')[0]
    return s

def get_score_pitching(col):
    s = col.split('-')[1]
    return s

def change_bat_outcome(col):

    if str(col)[0] in ('O','R'):
        return col
    else:
        return 'B'

def remove_pct(col):

    s = col
    s = s.replace('%','')
    return s

def get_table(soup):
    temp = soup.find('div',{'id':'all_play_by_play'})
    temp2 = bs4.BeautifulSoup(str(temp).replace('<!--',''), 'html.parser')
    table = temp2.find('table',{'id':'play_by_play'})

    df = pd.read_html(str(table), header=0, )[0]
    df = df[(df['Out'].str.contains('Top')==False) & (df['Out'].str.contains('Bottom')==False)]

    df['year'] = year
    df['doubleHeader'] = doubleHeader
    df['date'] = date
    df['gameKey'] = gameKey
    df['homeTeamAbbr'] = homeTeam
    df['awayTeamAbbr'] = awayTeam
    df['numPitch'] = df['Pit(cnt)'].apply(change_num_pitch)
    df['numBalls'] = df['Pit(cnt)'].apply(change_pit_balls)
    df['numStrikes'] = df['Pit(cnt)'].apply(change_pit_strikes)
    df['batterNameKey'] = df['Batter'].apply(get_nameKey)
    df['pitcherNameKey'] = df['Pitcher'].apply(get_nameKey)
    df['scoreTeamAtBat'] = df['Score'].apply(get_score_batting)
    df['scoreTeamAtPitch'] = df['Score'].apply(get_score_pitching)
    df['atBatOutcome'] = df['R/O'].apply(change_bat_outcome)
    df['wWPA'] = df['wWPA'].apply(remove_pct)
    df['wWE'] = df['wWE'].apply(remove_pct)

    keepCols = ['gameKey', 'date','year', 'homeTeamAbbr','awayTeamAbbr','Inn', '@Bat','scoreTeamAtBat', 'scoreTeamAtPitch','Batter',
       'Pitcher',  'Out',
            'numPitch', 'numBalls', 'numStrikes', 'RoB',  'atBatOutcome',  'wWPA', 'wWE', 'Play Description','batterNameKey', 'pitcherNameKey']


    df = df[keepCols]

    nameCols = ['gameKey', 'date','year', 'homeTeamAbbr','awayTeamAbbr','inn', 'teamAtBat','scoreTeamAtBat', 'scoreTeamAtPitch','batter',
       'pitcher',   'out',
            'numPitch', 'ball', 'strike', 'runnerOnBase',  'atBatOutcome',  'wWPA', 'wWE', 'playDescription','batterNameKey', 'pitcherNameKey']
    df.columns = nameCols
    return df

##################################################################
##################################################################


conn = sqlite3.connect('mlb_salary_comp_v2.db')
cur = conn.cursor()

refNames = pd.read_sql_query("""
SELECT DISTINCT name, nameKey
FROM meta
; """, conn)

nameDict = {}
for name, nameKey in zip(refNames.name, refNames.nameKey):
    nameDict[name] = nameKey

##################################################################
##########  Create tables in the database
##################################################################

cur.execute(
"""
DROP TABLE IF EXISTS games_play_by_play;
""")



cur.execute(
"""
CREATE TABLE games_play_by_play (
gameKey TEXT,
date TEXT,
year INTEGER,
homeTeamAbbr TEXT,
awayTeamAbbr TEXT,
inn TEXT,
teamAtBat TEXT,
scoreTeamAtBat INTEGER,
scoreTeamAtPitch INTEGER,
batter TEXT,
pitcher TEXT,
out INTEGER,
numPitch INTEGER,
ball INTEGER,
strike INTEGER,
runnerOnBase TEXT,
atBatOutcome TEXT,
wWPA INTEGER,
wWE INTEGER,
playDescription TEXT,
batterNameKey TEXT,
pitcherNameKey TEXT
);
""")
##################################################################
##################################################################


counter = 0
df = pd.DataFrame()

for year in range(2000,2020):
    year = str(year)

    url = 'https://www.baseball-reference.com/leagues/MLB/' + year + '-schedule.shtml'
    res = requests.get(url)
    soup=bs4.BeautifulSoup(res.text, 'html.parser')

    content = soup.find('div',{'class': "section_content"})

    for divs in content('div'):
        h = divs.find('h3')
        games = divs('p', {'class':'game'})
        for p in games:
            a1 = p('a')[0]
            a2 = p('a')[1]

            boxscore = p.find('em')
            boxscoreUrl = boxscore.find('a')['href']

            boxUrl = 'https://www.baseball-reference.com/' + boxscoreUrl

            boxRes = requests.get(boxUrl)
            boxSoup=bs4.BeautifulSoup(boxRes.text, 'html.parser')

            boxMeta = boxSoup.find('div',{'class':'scorebox_meta'})

            startTime = boxMeta('div')[1].text.split(': ')[1]



            date = datetime.strptime(h.text, '%A, %B %d, %Y').strftime("%Y-%m-%d")
            homeTeam = a2['href'].split('/')[2]
            awayTeam = a1['href'].split('/')[2]
            doubleHeader = boxscoreUrl.replace('.shtml','')[-1]
            gameKey = date.replace('-','') + homeTeam + awayTeam + doubleHeader

            dayOfWeek= h.text.split(',')[0]
            month = h.text.split()[1]

            df = df.append(get_table(boxSoup))
            counter += 1

            elapsed_ = time.perf_counter() - start
            hours   = floor(elapsed_ / 60**2)
            minutes = floor((elapsed_ - hours*60**2) / 60)
            seconds = floor(elapsed_ - hours*60**2 -minutes*60)

            print(counter, date, ' - ', awayTeam + ' @ ' + homeTeam, ' - ',  'Elapsed Time:',  hours, 'hours', minutes, 'minutes', seconds, 'seconds')

            if counter % 100 ==0:

                df.to_sql('games_play_by_play', con=conn, if_exists='append', index=False)
                df = pd.DataFrame()



df.to_sql('games_play_by_play', con=conn, if_exists='append', index=False)
#df.to_csv('games_schedules.csv', mode='w', header = True, index = False)
