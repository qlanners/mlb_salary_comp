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

def try_INT_or_zero(x):
    try:
        return int(x)
    except:
        return 0
#lists for personal attributes

NAME = []
NAME_KEY = []

YEAR = []
TEAM = []
POSITION = []
GAMES = []



TEAM_1 = []
TEAM_1_GAMES = []
TEAM_2 = []
TEAM_2_GAMES = []
TEAM_3 = []
TEAM_3_GAMES = []
TEAM_4 = []
TEAM_4_GAMES = []
TEAM_5 = []
TEAM_5_GAMES = []
TEAM_6 = []
TEAM_6_GAMES = []
DAYS_BW_TEAM_GAMES_MEAN = []
DAYS_BW_TEAM_GAMES_STDEV = []

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
        positions = []

        for item in body.find_all('a', href=True):
            #players_urls.append(item['href'])
            players_namekeys.append(item['href'][11:-6])
            names.append(item.text)

        for item in body.find_all('td', {'data-stat':'pos'}):
            positions.append(item.text)



        #start loop for each players

        for namekey, name, _pos in zip(players_namekeys, names, positions):

            try_counter += 1

            try:

                ### Player's Level - Game Level - Batting Statistics

                url_PG = "https://www.baseball-reference.com/players/gl.fcgi?id=" + namekey + "&t=f&year=" + year
                res_PG = requests.get(url_PG)
                soup_PG=bs4.BeautifulSoup(res_PG.text, 'html.parser')
                foot = soup_PG.find('tfoot')
                body = soup_PG.find('tbody')
                body_TEAMID = body.find_all('td', {'data-stat':'team_ID'})
                body_GTM = body.find_all('td', {'data-stat':'team_game_num'})

                team_id = []
                game_result = []
                gtm = []
                days_rest = []
                days_bw_team_games = []

                for n in range(len(body_GTM)):

                    _team_id = body_TEAMID[n].text
                    _gtm = int(body_GTM[n].text.split('(')[0])

                    if n == 0:
                        _days_bw_team_games = _gtm
                    else:
                        _days_bw_team_games = _gtm - gtm[-1]

                    team_id.append(_team_id)
                    gtm.append(_gtm)
                    days_bw_team_games.append(_days_bw_team_games)

                team_id_dict = Counter(team_id)

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
                POSITION.append(_pos)

                TEAM_1.append(list(team_id_dict.keys())[0])
                TEAM_1_GAMES.append(team_id_dict[list(team_id_dict.keys())[0]])
                try:
                    TEAM_2.append(list(team_id_dict.keys())[1])
                    TEAM_2_GAMES.append(team_id_dict[list(team_id_dict.keys())[1]])
                except:
                    TEAM_2.append('NA')
                    TEAM_2_GAMES.append('NA')

                try:
                    TEAM_3.append(list(team_id_dict.keys())[2])
                    TEAM_3_GAMES.append(team_id_dict[list(team_id_dict.keys())[2]])
                except:
                    TEAM_3.append('NA')
                    TEAM_3_GAMES.append('NA')

                try:
                    TEAM_4.append(list(team_id_dict.keys())[3])
                    TEAM_4_GAMES.append(team_id_dict[list(team_id_dict.keys())[3]])
                except:
                    TEAM_4.append('NA')
                    TEAM_4_GAMES.append('NA')

                try:
                    TEAM_5.append(list(team_id_dict.keys())[4])
                    TEAM_5_GAMES.append(team_id_dict[list(team_id_dict.keys())[4]])
                except:
                    TEAM_5.append('NA')
                    TEAM_5_GAMES.append('NA')

                try:
                    TEAM_6.append(list(team_id_dict.keys())[5])
                    TEAM_6_GAMES.append(team_id_dict[list(team_id_dict.keys())[5]])
                except:
                    TEAM_6.append('NA')
                    TEAM_6_GAMES.append('NA')

                GAMES.append(len(body_GTM))
                DAYS_BW_TEAM_GAMES_MEAN.append(stat.mean(days_bw_team_games))
                DAYS_BW_TEAM_GAMES_STDEV.append(stat.stdev(days_bw_team_games)  if len(set(days_bw_team_games)) > 1 else 0)

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

                elapsed_ = perf_counter() - start

                hours   = floor(elapsed_ / 60**2)
                minutes = floor((elapsed_ - hours*60**2) / 60)
                seconds = floor(elapsed_ - hours*60**2 -minutes*60)

                print(try_counter, '- success', '- ',team, '- ', year, '- ', name, ' ', _pos, ' ', 'Elapsed Time:',  hours, 'hours', minutes, 'minutes', seconds, 'seconds')

            except:

                miss_counter += 1


                misses.write(str(miss_counter) + team + '- ' + year + '- ' + name + ' ' + _pos + ' - ' + url_PG + '\n')

                elapsed_ = perf_counter() - start

                hours   = floor(elapsed_ / 60**2)
                minutes = floor((elapsed_ - hours*60**2) / 60)
                seconds = floor(elapsed_ - hours*60**2 -minutes*60)

                print(try_counter, '- miss', '- ',team, '- ', year,'- ', name, ' ',_pos, ' ', 'Elapsed Time:',  hours, 'hours', minutes, 'minutes', seconds, 'seconds')





misses.close()



#Create the csv output  (think about adding the team)

data_dict = {
'NAME': NAME,
"NAME_KEY": NAME_KEY,
"YEAR": YEAR,
"TEAM": TEAM,
"POSITION": POSITION,
"GAMES": GAMES,
"TEAM_1": TEAM_1,
"TEAM_1_GAMES": TEAM_1_GAMES,
"TEAM_2": TEAM_2,
"TEAM_2_GAMES": TEAM_2_GAMES,
"TEAM_3": TEAM_3,
"TEAM_3_GAMES": TEAM_3_GAMES,
"TEAM_4": TEAM_4,
"TEAM_4_GAMES": TEAM_4_GAMES,
"TEAM_5": TEAM_5,
"TEAM_5_GAMES": TEAM_5_GAMES,
"TEAM_6": TEAM_6,
"TEAM_6_GAMES": TEAM_6_GAMES,
"DAYS_BW_TEAM_GAMES_MEAN": DAYS_BW_TEAM_GAMES_MEAN,
"DAYS_BW_TEAM_GAMES_STDEV": DAYS_BW_TEAM_GAMES_STDEV,
"POSITION_MODE": POSITION_MODE,
"CAT": CAT,
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

columns =[\
'NAME',\
"NAME_KEY",\
"YEAR",\
"TEAM",\
"POSITION",\
"GAMES",\
"DAYS_BW_TEAM_GAMES_MEAN",\
"DAYS_BW_TEAM_GAMES_STDEV",\
"TEAM_1",\
"TEAM_1_GAMES",\
"TEAM_2",\
"TEAM_2_GAMES",\
"TEAM_3",\
"TEAM_3_GAMES",\
"TEAM_4",\
"TEAM_4_GAMES",\
"TEAM_5",\
"TEAM_5_GAMES",\
"TEAM_6",\
"TEAM_6_GAMES",\
"POSITION_MODE",\
"CAT",\
"FSTBASE",\
"SCDBASE",\
"TRDBASE",\
"SSTOP",\
"LFTFLD",\
"CTRFLD",\
"RGTFLD",\
"DESGHIT",\
"PNCHHIT",\
"PNCHRUN",\
"PITCHER",\
"INGS",\
"INGS_MEAN",\
"INGS_STDEV",\
"PO",\
"PO_MEAN",\
"PO_STDEV",\
"ASTS",\
"ASTS_MEAN",\
"ASTS_STDEV",\
"ERR",\
"ERR_MEAN",\
"ERR_STDEV"]

df = pd.DataFrame(data_dict, columns=columns)
df.to_csv('fielding.csv', mode='w', header = True, index = False)
