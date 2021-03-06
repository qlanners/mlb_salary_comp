# combined scraper

import requests
import bs4
import pandas as pd
from time import perf_counter
from math import floor

'''
The objective of this scraper is
to grab, for each player, for each year,
those who missed games due to disciplinary measures
'''

def remove_dot(col):
    if not pd.isnull(col):
        return col.replace('• ','')
    else:
        return col

start = perf_counter()

#scrapers = ['Disciplinary', 'Personal', 'Injuries', 'DL', 'Minors']
scrapers = 'Minors'

count_scraper = 0

for scraper in scrapers:
    count_scraper += 1


    urlStart = "http://www.prosportstransactions.com/baseball/Search/"
    urlEnd = "SearchResults.php?Player=&Team=&BeginDate=1999-10-28&EndDate=2019-10-01&" + scraper + "ChkBx=yes&submit=Search"
    url = urlStart + urlEnd



    res = requests.get(url)
    soup=bs4.BeautifulSoup(res.text, 'html.parser')
    body, refs = soup('table')

    aHrefs = [url]
    for a in refs('a')[:-1]:
        ref = a['href']
        aHrefs.append(urlStart + ref)

    links = [aHrefs[52], aHrefs[110], aHrefs[137], aHrefs[3327]]
    linksSize = len(links)
    counter = -1

    column_names = ['Date', 'Team', 'Acquired', 'Relinquished', 'Notes']
    df = pd.DataFrame(columns = column_names)

    misses = open('missedGames' + scraper + 'Misses_2.txt', 'w')

    for u in links:

        counter += 1

        try:
            _res = requests.get(u)
            _soup=bs4.BeautifulSoup(_res.text, 'html.parser')
            _body= _soup('table')[0]

            dfs = pd.read_html(str(_body), header=0)
            _df = dfs[0]


            df = df.append(_df)

            elapsed_ = perf_counter() - start

            hours   = floor(elapsed_ / 60**2)
            minutes = floor((elapsed_ - hours*60**2) / 60)
            seconds = floor(elapsed_ - hours*60**2 -minutes*60)

            print('scraper: ',scraper, '---', count_scraper, 'of 5,', "page", counter, 'of ',linksSize-1, 'Elapsed Time:',  hours, 'hours', minutes, 'minutes', seconds, 'seconds')
            print(u)
        except:

            misses.write(str(counter) + ' ' + u  + '\n')

    misses.close()

    df['Acquired'] = df['Acquired'].apply(remove_dot)
    df['Relinquished'] = df['Relinquished'].apply(remove_dot)
    df.to_csv('missedGames' + scraper +'_2.csv', mode='w', header = True, index = False)


    elapsed_ = perf_counter() - start

    hours   = floor(elapsed_ / 60**2)
    minutes = floor((elapsed_ - hours*60**2) / 60)
    seconds = floor(elapsed_ - hours*60**2 -minutes*60)

print('========= DONE ==========', '\nElapsed Time:',  hours, 'hours', minutes, 'minutes', seconds, 'seconds')
