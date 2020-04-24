import requests
import bs4
import pandas as pd
from time import perf_counter
from math import floor

tempCols = ['rk', 'team', 'league', 'numGames', 'win','loss','winLossPct',
            'runsScoredAllowed', 'runsAllowed', 'runsDiff', 'strOfSched',
           'simpRateSys','pythagWinLoss', 'luck','vsEast', 'vsCent','vsWest',
            'inter', 'atHome', 'onRoad', 'exInn', 'oneRun', 'vsRhp', 'vsLhp',
           'grOrEqThan500', 'lowThan500', 'year']
colsReorg = ['year', 'rk', 'team', 'league', 'numGames', 'win','loss','winLossPct',
            'runsScoredAllowed', 'runsAllowed', 'runsDiff', 'strOfSched',
           'simpRateSys','pythagWinLoss', 'luck','vsEast', 'vsCent','vsWest',
            'inter', 'atHome', 'onRoad', 'exInn', 'oneRun', 'vsRhp', 'vsLhp',
           'grOrEqThan500', 'lowThan500']

df = pd.DataFrame(columns = colsReorg)

for year in range(1995,2020):
    url = 'https://www.baseball-reference.com/leagues/MLB/' + str(year) + '-standings.shtml'
    res = requests.get(url)
    soup=bs4.BeautifulSoup(res.text, 'html.parser')
    container = soup.find('div', {'id': "all_expanded_standings_overall"})
    soup2=bs4.BeautifulSoup(list(container)[5], 'html.parser')
    table = soup2.find('table')

    dfs = pd.read_html(str(table), header=0)
    _df = dfs[0]
    _df['year'] = year
    if year == 2019:
        _df = _df.drop(['Strk','last10','last20','last30'], axis=1)


    _df.columns = tempCols
    _df = _df[colsReorg]

    df = df.append(_df)

    print(year, 'done')

df['team'] = df['team'].apply(lambda x: x[-3:])
df.to_csv('teams_standings.csv', index=False)
