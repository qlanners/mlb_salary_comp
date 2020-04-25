import requests
import bs4
import pandas as pd

cols = ['C', '1B', '2B', '3B', 'SS','LF','CF','RF','DH']

dataDict = {}
dataDict['team'] = []
dataDict['year'] = []
dataDict['name'] = []
dataDict['nameKey'] = []
dataDict['pos'] = []

for year in range(2000,2020):
    url = 'https://www.baseball-reference.com/leagues/MLB/' + str(year) + '-team-starting-lineups.shtml'
    res = requests.get(url)
    soup=bs4.BeautifulSoup(res.text, 'html.parser')

    tbody = soup.find('tbody')
    table = soup.find('table')



    for tr in tbody('tr'):
        for a, t in zip(tr.find_all('a')[1:], cols):
            dataDict['team'].append(tr.find('a').text)
            dataDict['year'].append(year)
            dataDict['name'].append(a.text)
            dataDict['nameKey'].append(a['href'][11:-6])
            dataDict['pos'].append(t)
            #print(tr.find('a').text, a.text, a['href'][11:-6], t)

    print(year, 'done')

columns = ['team','year', 'name', 'nameKey', 'pos']
df = pd.DataFrame(dataDict, columns = columns)

df.to_csv('teams_starters.csv', index=False)
