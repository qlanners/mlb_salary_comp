import requests
import bs4
from collections import Counter
import statistics as stat
import pandas as pd
from time import perf_counter
from math import floor
'''
The objective of this scraper is
to grab, for each player, for each year,
the number of games played at each position
'''

start = perf_counter()

def _mode(lst):
    counter = Counter(lst)
    _,val = counter.most_common(1)[0]
    return [x for x,y in counter.items() if y == val]

#lists for personal attributes

NAME = []
NAME_KEY = []

YEAR = []
TEAM = []

#lists for positions played

CAT = []
FSTBASE = []
SCDBASE = []
TRDBASE = []
SSTOP = []
LFTFLD = []
CTRFLD = []
RGTFLD = []
DESGHIT = []
PNCHHIT = []
PNCHRUN = []
PITCHER = []
POSITION_MODE = []

#lists for fielding stats

INGS = []
INGS_MEAN = []
INGS_STDEV = []

PO = []
PO_MEAN = []
PO_STDEV = []

ASTS = []
ASTS_MEAN = []
ASTS_STDEV = []

ERR = []
ERR_MEAN = []
ERR_STDEV = []

miss_counter = 0
try_counter = 0

misses = open('fielding_misses.txt', 'w')

for year in range(2000,2020):
    year = str(year)

    url_L = "https://www.baseball-reference.com/leagues/MLB/" + year + ".shtml"
    res_L = requests.get(url_L)
    soup_L=bs4.BeautifulSoup(res_L.text, 'html.parser')
    body_L = soup_L.find('tbody')

    teams_urls = []
    for item in body_L.find_all('a', href=True):
        teams_urls.append(item['href'])


    for url_team in teams_urls:

        url_T = 'https://www.baseball-reference.com' + url_team
        res_T = requests.get(url_T)
        soup_T=bs4.BeautifulSoup(res_T.text, 'html.parser')
        body = soup_T.find('tbody')

        #get urls and namekeys for all players listed in that team for that year
        #players_urls = []

        team = soup_T.find('h1', {'itemprop':'name'}).find_all('span')[1].text
        players_namekeys = []
        names = []

        for item in body.find_all('a', href=True):
            #players_urls.append(item['href'])
            players_namekeys.append(item['href'][11:-6])
            names.append(item.text)



        #start loop for each players

        for namekey, name in zip(players_namekeys, names):

            try_counter += 1

            try:

                ### Player's Level - Game Level - Batting Statistics

                url_PG = "https://www.baseball-reference.com/players/gl.fcgi?id=" + namekey + "&t=f&year=" + year
                res_PG = requests.get(url_PG)
                soup_PG=bs4.BeautifulSoup(res_PG.text, 'html.parser')
                foot = soup_PG.find('tfoot')

                #get positions played

                pos = []
                for p in soup_PG.find_all('td', {'data-stat':'pos_game'}):

                    for s in p.text.split(' '):
                        pos.append(s)

                pos_dict = Counter(pos)

                C  = pos_dict['C']  if 'C'  in pos_dict.keys() else 0
                FB = pos_dict['1B'] if '1B' in pos_dict.keys() else 0
                SB = pos_dict['2B'] if '2B' in pos_dict.keys() else 0
                TB = pos_dict['3B'] if '3B' in pos_dict.keys() else 0
                SS = pos_dict['SS'] if 'SS' in pos_dict.keys() else 0
                LF = pos_dict['LF'] if 'LF' in pos_dict.keys() else 0
                CF = pos_dict['CF'] if 'CF' in pos_dict.keys() else 0
                RF = pos_dict['RF'] if 'RF' in pos_dict.keys() else 0
                DH = pos_dict['DH'] if 'DH' in pos_dict.keys() else 0
                PH = pos_dict['PH'] if 'PH' in pos_dict.keys() else 0
                PR = pos_dict['PR'] if 'PR' in pos_dict.keys() else 0
                P =  pos_dict['P']  if 'P'  in pos_dict.keys() else 0
                position_mode = _mode(pos)
                #get fieding statistics

                inn = []
                for p in soup_PG.find_all('td', {'data-stat':'Inn_def'})[:-1]:
                    inn.append(float(p.text))

                ings = float(foot.find('td',{'data-stat':'Inn_def'}).text)
                ings_mean = stat.mean(inn)
                ings_stdev = stat.stdev(inn)  if len(set(inn)) > 1 else 0

                po = []
                for p in soup_PG.find_all('td', {'data-stat':'PO'})[:-1]:
                    po.append(int(p.text))

                putouts = int(foot.find('td',{'data-stat':'PO'}).text)
                putouts_mean = stat.mean(po)
                putouts_stdev = stat.stdev(po)  if len(set(po)) > 1 else 0

                ast = []
                for p in soup_PG.find_all('td', {'data-stat':'A'})[:-1]:
                    ast.append(int(p.text))

                asts = foot.find('td',{'data-stat':'A'}).text
                asts_mean = stat.mean(ast)
                asts_stdev = stat.stdev(ast)  if len(set(ast)) > 1 else 0

                err = []
                for p in soup_PG.find_all('td', {'data-stat':'E_def'})[:-1]:
                    err.append(int(p.text))

                errors = int(foot.find('td',{'data-stat':'E_def'}).text)
                errors_mean = stat.mean(err)
                errors_stdev = stat.stdev(err)  if len(set(err)) > 1 else 0


                NAME.append(name)
                NAME_KEY.append(namekey)
                YEAR.append(year)

                TEAM.append(team)

                CAT.append(C)
                FSTBASE.append(FB)
                SCDBASE.append(SB)
                TRDBASE.append(TB)
                SSTOP.append(SS)
                LFTFLD.append(LF)
                CTRFLD.append(CF)
                RGTFLD.append(RF)
                DESGHIT.append(DH)
                PNCHHIT.append(PH)
                PNCHRUN.append(PR)
                PITCHER.append(P)
                POSITION_MODE.append(position_mode)

                INGS.append(ings)
                INGS_MEAN.append(ings_mean)
                INGS_STDEV.append(ings_stdev)
                PO.append(putouts)
                PO_MEAN.append(putouts_mean)
                PO_STDEV.append(putouts_stdev)
                ASTS.append(asts)
                ASTS_MEAN.append(asts_mean)
                ASTS_STDEV.append(asts_stdev)
                ERR.append(errors)
                ERR_MEAN.append(errors_mean)
                ERR_STDEV.append(errors_stdev)

                print(try_counter, '- success', '- ',year, ' ', perf_counter() - start)

            except:

                miss_counter += 1


                misses.write(str(miss_counter) + ' - ' + url_PG + '\n')

                print(try_counter, '- miss', '- ', name)





misses.close()



#Create the csv output  (think about adding the team)

data_dict = {
"NAME": NAME,
"NAME_KEY": NAME_KEY,
"TEAM": TEAM,
"YEAR": YEAR,
"CAT": CAT,
"POSITION_MODE": POSITION_MODE,
"FSTBASE": FSTBASE,
"SCDBASE": SCDBASE,
"TRDBASE": TRDBASE,
"SSTOP": SSTOP,
"LFTFLD": LFTFLD,
"CTRFLD": CTRFLD,
"RGTFLD": RGTFLD,
"DESGHIT": DESGHIT,
"PNCHHIT": PNCHHIT,
"PNCHRUN": PNCHRUN,
"PITCHER": PITCHER,
"INGS": INGS,
"INGS_MEAN": INGS_MEAN,
"INGS_STDEV": INGS_STDEV,
"PO": PO,
"PO_MEAN": PO_MEAN,
"PO_STDEV": PO_STDEV,
"ASTS": ASTS,
"ASTS_MEAN": ASTS_MEAN,
"ASTS_STDEV": ASTS_STDEV,
"ERR": ERR,
"ERR_MEAN": ERR_MEAN,
"ERR_STDEV": ERR_STDEV
}

df = pd.DataFrame(data_dict)
df.to_csv('fielding.csv', mode='w', header = True, index = False)


end = perf_counter()
elapsed = end - start

hours   = floor(elapsed / 60**2)
minutes = floor((elapsed - hours*60**2) / 60)
seconds = floor(elapsed - hours*60**2 -minutes*60)

fielding_runtime = open('fielding_runtime.txt', mode = 'w')
fielding_runtime.write('\n ++++++++++++++++++++++++++++++++++++++++ END ++++++++++++++++++++++++++++++++++++++++ \n')
fielding_runtime.write(f'\n Elapsed Time:  {hours} hours, {minutes} minutes, {seconds} seconds \n Number of players tried: {try_counter}\n Number of misses: {miss_counter}')
fielding_runtime.close()
