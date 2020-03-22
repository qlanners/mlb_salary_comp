# Spotrac Salary scraper

import requests
import bs4
import pandas as pd
from time import perf_counter
from math import floor

start = perf_counter()

YEAR = []
TEAM = []
PLAYER = []
INJURED = []
AGE = []
POS = []
STATUS = []
BASE_SALARY = []
PAYROLL_SALARY = []
ADJ_SALARY = []
LUX_TAX_SALARY = []
PLAYER_URL = []
TEAM_URL = []


#start by getting all the teams and their url for each year
# then, go into each team url and grab player data
# loop for years 2000 to 2019 inclusively

for year in range(2000,2020):

    url_year = "https://www.spotrac.com/mlb/payroll/" + str(year)
    res_year = requests.get(url_year)
    soup_year=bs4.BeautifulSoup(res_year.text, 'html.parser')
    body = soup_year('tr')


    for b in body:

        if b.find('td', class_="player noborderleft") != None:

            td = b.find('td', class_="player noborderleft")

            team = td.find('a').text
            team_url = td.find('a')['href']


            #going into the team_url

            res = requests.get(team_url)
            soup=bs4.BeautifulSoup(res.text, 'html.parser')

            body = soup('tbody')
            headers = soup('header', class_='team-header')

            players_soup = body[0].find_all('td',class_='player')
            right_soup = body[0].find_all('td',class_='right')
            center_soup = body[0].find_all('td',class_='center')


            for na,ag,po,st,bs,ps,as_,lux in zip( players_soup,
                                           center_soup[::5],
                                           center_soup[1::5],
                                           center_soup[2::5],
                                           right_soup[::5],
                                           right_soup[3::5],
                                           right_soup[4::5],
                                           center_soup[4::5]):
                injured = 0

                YEAR.append(str(year))
                TEAM.append(team)
                PLAYER.append(na.find('a').text)
                INJURED.append(str(injured))
                AGE.append(ag.text.strip())
                POS.append(po.text.strip())
                STATUS.append(st.text.strip())
                BASE_SALARY.append(bs.find('span').text.replace('$','').replace(',',''))
                PAYROLL_SALARY.append(ps.find('span').text.replace('$','').replace(',',''))
                ADJ_SALARY.append(as_.find('span').text.replace('$','').replace(',',''))
                LUX_TAX_SALARY.append(lux.text.strip().replace(',',''))
                PLAYER_URL.append(na.find('a')['href'])
                TEAM_URL.append(team_url)



            if headers[0].find('h2').text.split()[1] == 'Injured':

                players_soup = body[1].find_all('td',class_='player')
                right_soup = body[1].find_all('td',class_='right')
                center_soup = body[1].find_all('td',class_='center')

                for na,ag,po,st,bs,ps,as_,lux in zip( players_soup,
                                           center_soup[::5],
                                           center_soup[1::5],
                                           center_soup[2::5],
                                           right_soup[::5],
                                           right_soup[3::5],
                                           right_soup[4::5],
                                           center_soup[4::5]):
                    injured = 1


                    YEAR.append(str(year))
                    TEAM.append(team)
                    PLAYER.append(na.find('a').text)
                    INJURED.append(str(injured))
                    AGE.append(ag.text.strip())
                    POS.append(po.text.strip())
                    STATUS.append(st.text.strip())
                    BASE_SALARY.append(bs.find('span').text.replace('$','').replace(',',''))
                    PAYROLL_SALARY.append(ps.find('span').text.replace('$','').replace(',',''))
                    ADJ_SALARY.append(as_.find('span').text.replace('$','').replace(',',''))
                    LUX_TAX_SALARY.append(lux.text.strip().replace(',',''))
                    PLAYER_URL.append(na.find('a')['href'])
                    TEAM_URL.append(team_url)


            elapsed_ = perf_counter() - start
            hours   = floor(elapsed_ / 60**2)
            minutes = floor((elapsed_ - hours*60**2) / 60)
            seconds = floor(elapsed_ - hours*60**2 -minutes*60)

            print(year,team, 'Elapsed Time:',  hours, 'hours', minutes, 'minutes', seconds, 'seconds')

data_dict = {
"YEAR": YEAR,
'TEAM': TEAM,
'PLAYER':PLAYER,
'INJURED': INJURED,
'AGE': AGE,
'POS': POS,
'STATUS': STATUS,
'BASE_SALARY': BASE_SALARY,
'PAYROLL_SALARY': PAYROLL_SALARY,
'ADJ_SALARY': ADJ_SALARY,
'LUX_TAX_SALARY': LUX_TAX_SALARY,
'PLAYER_URL': PLAYER_URL,
'TEAM_URL': TEAM_URL}

columns = [
"YEAR",
'TEAM',
'PLAYER',
'INJURED',
'AGE',
'POS',
'STATUS',
'BASE_SALARY',
'PAYROLL_SALARY',
'ADJ_SALARY',
'LUX_TAX_SALARY',
'PLAYER_URL',
'TEAM_URL'
]

df = pd.DataFrame(data_dict, columns=columns)
df.to_csv('salary_spotrac.csv', mode='w', header = True, index = False)
