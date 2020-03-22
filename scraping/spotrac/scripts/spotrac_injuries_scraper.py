# Spotrac Injuries scraper

import requests
import bs4
import pandas as pd
from time import perf_counter
from math import floor

start = perf_counter()

PLAYER = []
INJ_START_DT = []
INJ_END_DT = []
TEAM = []
REASON = []
DAYS_MISSED = []
CASH_PAID_WHILE_INJ = []
PLAYER_URL = []

df_inj = pd.read_csv('../data/salary_spotrac.csv')
inj = df_inj[df_inj['INJURED']==1]
inj = inj.drop_duplicates(subset=['PLAYER','PLAYER_URL'])
list_of_inj_players = list(zip(inj.PLAYER, inj.PLAYER_URL))

num_of_inj = len(list_of_inj_players)
counter = 0

for u in list_of_inj_players:
    counter += 1

    url = u[1] + 'injuries'
    res = requests.get(url)
    soup=bs4.BeautifulSoup(res.text, 'html.parser')

    body_injury = soup.find('h2',text='Injuries').findNext('tbody')
    tr = body_injury.find_all('tr')

    for t in tr:
        td = t.find_all('td')
        dates = td[0].text.split(' - ')

        PLAYER.append(u[0])
        INJ_START_DT.append(dates[0])
        INJ_END_DT.append(dates[1])
        TEAM.append(td[1].text)
        REASON.append(td[2].text)
        DAYS_MISSED.append(td[3].text)
        CASH_PAID_WHILE_INJ.append(td[4].text.replace('$','').replace(',',''))
        PLAYER_URL.append(u[1])

    elapsed_ = perf_counter() - start
    hours   = floor(elapsed_ / 60**2)
    minutes = floor((elapsed_ - hours*60**2) / 60)
    seconds = floor(elapsed_ - hours*60**2 -minutes*60)

    print(counter, 'of', num_of_inj, u[0], 'Elapsed Time:',  hours, 'hours', minutes, 'minutes', seconds, 'seconds')

data_dict = {
'PLAYER': PLAYER,
'INJ_START_DT': INJ_START_DT,
'INJ_END_DT': INJ_END_DT,
'TEAM': TEAM,
'REASON': REASON,
'DAYS_MISSED': DAYS_MISSED,
'CASH_PAID_WHILE_INJ': CASH_PAID_WHILE_INJ,
'PLAYER_URL': PLAYER_URL
}

columns = [
'PLAYER',
'INJ_START_DT',
'INJ_END_DT',
'TEAM',
'REASON',
'DAYS_MISSED',
'CASH_PAID_WHILE_INJ',
'PLAYER_URL'
]

df = pd.DataFrame(data_dict, columns=columns)
df.to_csv('injuries_spotrac.csv', mode='w', header = True, index = False)
