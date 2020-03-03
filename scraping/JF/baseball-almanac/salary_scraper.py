# Salary scraper from baseball-almanac.completed

import requests
import bs4
import pandas as pd
import datetime as dt
from time import perf_counter
from math import floor

start = perf_counter()

df = pd.read_csv('list_of_players.csv')
df = df.drop_duplicates()
df = df[df['NAME_KEY'] == 'molinbe01']
#df = df[(df['NAME_KEY'].str.contains('\\.')) | (df['NAME_KEY'].str.contains("'"))]
#df = df.sample(50)

players_size = len(df.NAME_KEY)
counter = 0

NAME = []
NAME_KEY = []
YEAR = []
TEAM = []
UNIFORM_NUMBER = []
SALARY = []
ALL_STAR = []
WORLD_SERIES = []

misses = open('salary_misses.txt', 'w')

for name,key in zip(df.NAME,df.NAME_KEY):
    counter += 1

    try:
        player_key = key.replace('.','').replace("'",'')

        url = 'https://www.baseball-almanac.com/players/player.php?p=' + player_key

        res = requests.get(url)
        soup=bs4.BeautifulSoup(res.text, 'html.parser')

        tables = soup('table')
        teams_soup = tables[-9].find_all('td', class_="datacol")
        salaries_soup = tables[-9].find_all('td', class_="datacolR")
        uniform_num_soup = tables[-9].find_all('td', class_="datacolC")[0::3]
        all_star_soup = tables[-9].find_all('td', class_="datacolC")[1::3]
        world_series = tables[-9].find_all('td', class_="datacolC")[2::3]


        for t,s,u,a,w in zip(teams_soup, salaries_soup, uniform_num_soup, all_star_soup, world_series):
            year = t.text.split()[0]
            team = ' '.join(t.text.split()[1:])
            uniform =  u.text
            salary =  s.text.replace('$','').replace(',','').replace('.00','')
            if not salary.isnumeric():
                salary = 'NA'

            if a.text == 'Stats':
                all_star = 'yes'
            else:
                all_star = 'no'


            if w.text == 'Stats':
                world_series = 'yes'
            else:
                world_series = 'no'

            NAME.append(name)
            NAME_KEY.append(key)
            YEAR.append(year)
            TEAM.append(team)
            UNIFORM_NUMBER.append(uniform)
            SALARY.append(salary)
            ALL_STAR.append(all_star)
            WORLD_SERIES.append(world_series)

            elapsed_ = perf_counter() - start
            hours   = floor(elapsed_ / 60**2)
            minutes = floor((elapsed_ - hours*60**2) / 60)
            seconds = floor(elapsed_ - hours*60**2 -minutes*60)

        print(name, ' - ', counter, 'of', players_size,   ' - ', 'Elapsed Time:',  hours, 'hours', minutes, 'minutes', seconds, 'seconds')

    except:
        misses.write(name + '- ' +  url + '\n')
misses.close()

data_dict = {
'NAME': NAME,
'NAME_KEY': NAME_KEY,
'YEAR': YEAR,
'TEAM': TEAM,
'UNIFORM_NUMBER': UNIFORM_NUMBER,
'SALARY': SALARY,
'ALL_STAR': ALL_STAR,
'WORLD_SERIES': WORLD_SERIES}

columns = [
'NAME',
'NAME_KEY',
'YEAR',
'TEAM',
'UNIFORM_NUMBER',
'SALARY',
'ALL_STAR',
'WORLD_SERIES']

df = pd.DataFrame(data_dict, columns=columns)

df.to_csv('salaries_add.csv', mode='w', header = True, index = False)
