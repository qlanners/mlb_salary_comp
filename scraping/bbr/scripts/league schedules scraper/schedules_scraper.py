import requests
import bs4
import pandas as pd
from datetime import datetime
import time
from math import floor

'''
The objective of this scraper is
to grab, all game schedules for all seasons
'''
start = time.perf_counter()

GAMEKEYS = []
YEAR = []
MONTHS =[]
DAYOFWEEK = []
DATES_ALPHA = []
AWAYTEAMFULL = []
AWAYTEAMABRR = []
HOMETEAMFULL = []
HOMETEAMABRR = []
AWAYTEAMSCORE = []
HOMETEAMSCORE = []
STARTIME = []
ATTENDANCE = []
VENUE = []
DURATION = []
DOUBLEHEADER = []


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

        for bm in boxMeta('div'):
            for bms in bm('strong'):

                if bms.text.strip() == 'Attendance':
                    attendance = int(bm.text.split(': ')[1].replace(',',''))
                elif bms.text.strip() == 'Venue':
                    venue = bm.text.split(': ')[1]
                elif bms.text.strip() == 'Game Duration':
                    gameDur = bm.text.split(': ')[1]


        date = datetime.strptime(h.text, '%A, %B %d, %Y').strftime("%Y-%m-%d")
        homeTeam = a2['href'].split('/')[2]
        awayTeam = a1['href'].split('/')[2]
        doubleHeader = boxscoreUrl.replace('.shtml','')[-1]
        gameKey = date.replace('-','') + homeTeam + awayTeam + doubleHeader

        dayOfWeek= h.text.split(',')[0]
        month = h.text.split()[1]


        GAMEKEYS.append(gameKey)
        YEAR.append(year)
        MONTHS.append(month)
        DAYOFWEEK.append(dayOfWeek)
        DATES_ALPHA.append(date)
        AWAYTEAMFULL.append(a1.text)
        HOMETEAMFULL.append(a2.text)
        AWAYTEAMABRR.append(awayTeam)
        HOMETEAMABRR.append(homeTeam)
        AWAYTEAMSCORE.append(int(p.text.split('(')[1].split(')')[0]))
        HOMETEAMSCORE.append(int(p.text.split('(')[2].split(')')[0]))
        STARTIME.append(boxMeta('div')[1].text.split(': ')[1])
        ATTENDANCE.append(attendance)
        VENUE.append(venue)
        DURATION.append(gameDur)
        DOUBLEHEADER.append(doubleHeader)

        elapsed_ = time.perf_counter() - start
        hours   = floor(elapsed_ / 60**2)
        minutes = floor((elapsed_ - hours*60**2) / 60)
        seconds = floor(elapsed_ - hours*60**2 -minutes*60)

        print(date, ' - ', awayTeam + ' @ ' + homeTeam, ' - ',  'Elapsed Time:',  hours, 'hours', minutes, 'minutes', seconds, 'seconds')

columns = ['year', 'dateEng', 'date', 'startTime', 'awayTeam', 'awayTeamAbbr', 'homeTeam', 'homeTeamAbbr', 'awayTeamScore', 'homeTeamScore', 'venue', 'attendance', 'gameDuration']
dataDict = {}
dataDict['year'] = YEAR
dataDict['dateEng'] = DATES_ENGLISH
dataDict['date'] = DATES_ALPHA
dataDict['awayTeam'] = AWAYTEAMFULL
dataDict['awayTeamAbbr'] = AWAYTEAMABRR
dataDict['homeTeam'] = HOMETEAMFULL
dataDict['homeTeamAbbr'] = HOMETEAMABRR
dataDict['awayTeamScore'] = AWAYTEAMSCORE
dataDict['homeTeamScore'] = HOMETEAMSCORE
dataDict['startTime'] = STARTIME
dataDict['attendance'] = ATTENDANCE
dataDict['venue'] = VENUE
dataDict['gameDuration'] = DURATION

df = pd.DataFrame(dataDict, columns=columns)
df.to_csv('games_schedules.csv', mode='w', header = True, index = False)
