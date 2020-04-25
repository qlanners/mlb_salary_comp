import requests
import bs4
import pandas as pd

tempCols = ['rk', 'name', 'team', 'votePoints',  'league','year', 'award']
colsReorg = ['year', 'award', 'rk', 'name', 'team', 'league', 'votePoints']
df = pd.DataFrame(columns = colsReorg)

for year in range(2000,2020):
    url = 'https://www.baseball-reference.com/awards/awards_' + str(year) + '.shtml'
    res = requests.get(url)
    soup=bs4.BeautifulSoup(res.text, 'html.parser')

    AlMvp = soup.find('div', {'id': 'all_AL_MVP_voting'})
    NlMvp = soup.find('div', {'id': 'all_NL_MVP_voting'})
    AlCy = soup.find('div', {'id': 'all_AL_CYA_voting'})
    NlCy = soup.find('div', {'id': 'all_NL_CYA_voting'})
    AlRookie = soup.find('div', {'id': 'all_AL_ROY_voting'})
    NlRookie = soup.find('div', {'id': 'all_NL_ROY_voting'})
    AlManager = soup.find('div', {'id': 'all_AL_MOY_voting'})
    NlManager = soup.find('div', {'id': 'all_NL_MOY_voting'})

    tableAlMvp = bs4.BeautifulSoup(str(AlMvp).replace('<!--', ''), 'html.parser').find('table')
    tableNlMvp = bs4.BeautifulSoup(str(NlMvp).replace('<!--', ''), 'html.parser').find('table')
    tableAlCy = bs4.BeautifulSoup(str(AlCy).replace('<!--', ''), 'html.parser').find('table')
    tableNlCy = bs4.BeautifulSoup(str(NlCy).replace('<!--', ''), 'html.parser').find('table')
    tableAlRookie = bs4.BeautifulSoup(str(AlRookie).replace('<!--', ''), 'html.parser').find('table')
    tableNlRookie = bs4.BeautifulSoup(str(NlRookie).replace('<!--', ''), 'html.parser').find('table')
    tableAlManager = bs4.BeautifulSoup(str(AlManager).replace('<!--', ''), 'html.parser').find('table')
    tableNlManager = bs4.BeautifulSoup(str(NlManager).replace('<!--', ''), 'html.parser').find('table')

    divs = [AlMvp, NlMvp, AlCy, NlCy, AlRookie, NlRookie, AlManager, NlManager]
    tables = [tableAlMvp, tableNlMvp, tableAlCy, tableNlCy, tableAlRookie, tableNlRookie, tableAlManager, tableNlManager]

    for div, tab in zip(divs, tables):

        dfs = pd.read_html(str(tab), header=0)
        _df = dfs[0]
        colsKeep = list(_df.columns)[:4]
        _df =_df[colsKeep]
        _df['league'] = div.find('span')['data-label'][:2].replace(' ','')
        _df['year'] = year
        _df['award'] = div.find('span')['data-label'][3:-7].replace(' ','')
        _df.columns = tempCols

        _df = _df[colsReorg]

        df = df.append(_df)

    print(year, 'done')

df = df[df['rk']!='Rank']
typesDict={'year':'int64','votePoints':'float64' , 'rk':'int64'}
df = df.astype(typesDict)
print(df.dtypes)
df.to_csv('player_awards.csv', index=False)
