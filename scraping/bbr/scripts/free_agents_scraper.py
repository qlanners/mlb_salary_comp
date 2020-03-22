# free agency on baseball-reference
import requests
import bs4
import pandas as pd
import datetime as dt
from time import perf_counter
from math import floor

'''
The objective of this scraper is
to grab, for each player, for each year,
contractual information, mostly about free agency
'''
start = perf_counter()

NAME = []
NAME_KEY = []
YEAR = []
ARRIVAL_DT = []
ARRIVAL_METHOD = []
WAS_DRAFTED = []
DRAFT_ROUND = []
SIGNED_DT = []
BIRTHDATE = []
AGE_WHEN_SIGNED = []
FREE_AGENT_DT = []
PLAYER_URL = []
IS_FREE_AGENT_NOW = []
SEASON_START_DT = []


df = pd.read_csv('../JF/Baseball reference/meta_test.csv', usecols=['NAME', 'NAME_KEY', 'BIRTHDATE', 'YEAR'])
#df = df.sample(20)
df = df[['NAME', 'NAME_KEY', 'BIRTHDATE','YEAR']]
df['YEAR'] = df['YEAR'].astype(str)
df['concat_cols'] = df.apply(lambda x:'_'.join(x).split('_'), axis=1)


opening_dates_dict = {'2000': '2000-03-29',
                      '2001': '2001-04-01',
                      '2002': '2002-03-31',
                      '2003': '2003-03-30',
                      '2004': '2004-03-30',
                      '2005': '2005-04-03',
                      '2006': '2006-04-02',
                      '2007': '2007-04-01',
                      '2008': '2008-03-25',
                      '2009': '2009-04-05',
                      '2010': '2010-04-04',
                      '2011': '2011-03-31',
                      '2012': '2012-03-28',
                      '2013': '2013-03-31',
                      '2014': '2014-03-22',
                      '2015': '2015-04-05',
                      '2016': '2016-04-03',
                      '2017': '2017-04-02',
                      '2018': '2018-03-29',
                      '2019': '2019-03-20'}

players_size = len(df.concat_cols)
counter = 0

misses = open('../JF/Baseball reference/free_agent_misses.txt', 'w')

for item in df.concat_cols:

    try:
        counter += 1

        player_id = item[1]
        url = 'https://www.baseball-reference.com/players/' \
            + player_id[0] + '/' + player_id + '.shtml'



        res = requests.get(url)
        soup=bs4.BeautifulSoup(res.text, 'html.parser')
        new_soup_text = soup.find('h2',text='Transactions').findNext('div', class_ = 'placeholder').next_sibling.next_sibling
        new_soup = bs4.BeautifulSoup(new_soup_text, 'html.parser')

        free_agent = False

        all_p = new_soup('p')


        for s in all_p:

            if 'Free Agent' in s.text or 'free agent' in s.text:
                free_agent = True
                free_agent_dt = s.text.split(': ')[-2]
                free_agent_dt = dt.datetime.strptime(free_agent_dt, '%B %d, %Y').date()
                break
            if s.text.split(': ')[-1] == "Granted Free Agency.":
                free_agent = True
                free_agent_dt = s.text.split(': ')[-2]
                free_agent_dt = dt.datetime.strptime(free_agent_dt, '%B %d, %Y').date()
                break

        if not free_agent:
            free_agent_dt = 'restricted'

        for s in all_p:
            if 'Drafted' in s.text and 'Player signed' not in s.text:
                continue

            elif 'Drafted' in s.text and 'Player signed' in s.text:
                line = s.find_all('a', href=True)

                arrival_method = s.text.split(': ')[1].split()[0]
                arrival_dt = s.text.split(': ')[0]
                arrival_dt = dt.datetime.strptime(arrival_dt, '%B %d, %Y').date()
                signed_dt = s.text.split('Player signed ')[1].replace('.','')
                signed_dt = dt.datetime.strptime(signed_dt, '%B %d, %Y').date()
                draft_round = line[1].text
                break

            else:
                arrival_method = s.text.split(': ')[1].split()[0]
                arrival_dt = s.text.split(': ')[0]
                arrival_dt = dt.datetime.strptime(arrival_dt, '%B %d, %Y').date()
                signed_dt = s.text.split(': ')[0]
                signed_dt = dt.datetime.strptime(signed_dt, '%B %d, %Y').date()
                draft_round = 'not drafted'
                break

        if all_p[0].text.split(': ')[1].split()[0] == 'Drafted':
            was_drafted = 'yes'
        else:
            was_drafted = 'no'

        date1 = dt.datetime.strptime(str(signed_dt), '%Y-%m-%d')
        date2 = dt.datetime.strptime(item[2], '%Y-%m-%d')
        age_when_signed = int((date1 - date2).days / 365.2425)

        cond1 = dt.datetime.strptime(str(signed_dt), '%Y-%m-%d').date()>= dt.datetime.strptime('2016-12-14', '%Y-%m-%d').date()
        cond2 = arrival_method != 'Drafted'
        cond3 = age_when_signed <25

        if  cond1 and cond2 and cond3:
            free_agent_dt = 'restricted'

        is_free_agent_now = 'no'
        if arrival_method == 'Purchased':
            is_free_agent_now = 'yes'

        if free_agent:
            if dt.datetime.strptime(str(free_agent_dt), '%Y-%m-%d').date()<= dt.datetime.strptime(opening_dates_dict[str(item[-1])], '%Y-%m-%d').date():
                is_free_agent_now = 'yes'


        NAME.append(item[0])
        NAME_KEY.append(item[1])
        YEAR.append(item[-1])
        ARRIVAL_DT.append(str(arrival_dt))
        ARRIVAL_METHOD.append(arrival_method)
        WAS_DRAFTED.append(was_drafted)
        DRAFT_ROUND.append(draft_round)
        SIGNED_DT.append(str(signed_dt))
        BIRTHDATE.append(str(item[2]))
        AGE_WHEN_SIGNED.append(age_when_signed)
        FREE_AGENT_DT.append(str(free_agent_dt))
        IS_FREE_AGENT_NOW.append(is_free_agent_now)
        SEASON_START_DT.append(opening_dates_dict[str(item[-1])])
        PLAYER_URL.append(str(url))

        elapsed_ = perf_counter() - start
        hours   = floor(elapsed_ / 60**2)
        minutes = floor((elapsed_ - hours*60**2) / 60)
        seconds = floor(elapsed_ - hours*60**2 -minutes*60)

        print(item[0], ' - ', counter, 'of', players_size,   ' - ', 'Elapsed Time:',  hours, 'hours', minutes, 'minutes', seconds, 'seconds')

    except:
        misses.write(item[0] + '- ' + str(url)  + '\n')
misses.close()

data_dict = {
'NAME': NAME,
'NAME_KEY': NAME_KEY,
'YEAR': YEAR,
'ARRIVAL_DT': ARRIVAL_DT,
'ARRIVAL_METHOD': ARRIVAL_METHOD,
'WAS_DRAFTED': WAS_DRAFTED,
'DRAFT_ROUND': DRAFT_ROUND,
'SIGNED_DT': SIGNED_DT,
'BIRTHDATE': BIRTHDATE,
'AGE_WHEN_SIGNED': AGE_WHEN_SIGNED,
'FREE_AGENT_DT': FREE_AGENT_DT,
'IS_FREE_AGENT_NOW': IS_FREE_AGENT_NOW,
'SEASON_START_DT': SEASON_START_DT,
'PLAYER_URL': PLAYER_URL
}

columns = [
'NAME',
'NAME_KEY',
'YEAR',
'ARRIVAL_DT',
'ARRIVAL_METHOD',
'WAS_DRAFTED',
'DRAFT_ROUND',
'SIGNED_DT',
'BIRTHDATE',
'AGE_WHEN_SIGNED',
'FREE_AGENT_DT',
'IS_FREE_AGENT_NOW',
'SEASON_START_DT',
'PLAYER_URL'
]

df = pd.DataFrame(data_dict, columns=columns)

df.to_csv('free_agents_test.csv', mode='w', header = True, index = False)
