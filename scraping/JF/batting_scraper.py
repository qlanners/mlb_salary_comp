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
grab batting statistics
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

POSITION = []

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
#lists of pitching statistics
GAMES = []
DAYS_BW_TEAM_GAMES_MEAN = []
DAYS_BW_TEAM_GAMES_STDEV = []


#lists for batting stats
ATBATS = []
ATBATS_MEAN = []
ATBATS_STDEV = []
HITS = []
HITS_MEAN = []
HITS_STDEV = []
BASESONBALLS = []
BASESONBALLS_MEAN = []
BASESONBALLS_STDEV = []
HITBYPITCH = []
HITBYPITCH_MEAN = []
HITBYPITCH_STDEV = []
SINGLES = []
SINGLES_MEAN = []
SINGLES_STDEV = []
DOUBLES = []
DOUBLES_MEAN = []
DOUBLES_STDEV = []
TRIPLES = []
TRIPLES_MEAN = []
TRIPLES_STDEV = []
HOMERUNS = []
HOMERUNS_MEAN = []
HOMERUNS_STDEV = []
RBI = []
RBI_MEAN = []
RBI_STDEV = []
STRIKEOUT = []
STRIKEOUT_MEAN = []
STRIKEOUT_STDEV = []
SACRIFICE_F = []
BA_MEAN = []
BA_STDEV = []
OBP = []
OBP_MEAN = []
OBP_STDEV = []
SLG = []
SLG_MEAN = []
SLG_STDEV = []
WPA_MEAN = []
WPA_STDEV = []
BATRANK_1 = []
BATRANK_2 = []
BATRANK_3 = []
BATRANK_4 = []
BATRANK_5 = []
BATRANK_6 = []
BATRANK_7 = []
BATRANK_8 = []
BATRANK_9 = []
BATRANK_MODE = []

miss_counter = 0
try_counter = 0

misses = open('batting_misses.txt', 'w')

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

        for namekey, name, pos in zip(players_namekeys, names, positions):

            try_counter += 1

            try:

                ### Player's Level - Game Level - Batting Statistics


                url_PG = "https://www.baseball-reference.com/players/gl.fcgi?id=" + namekey + "&t=b&year=" + year
                res_PG = requests.get(url_PG)
                soup_PG=bs4.BeautifulSoup(res_PG.text, 'html.parser')

                body = soup_PG.find('tbody')
                body_TEAMID = body.find_all('td', {'data-stat':'team_ID'})
                body_GTM = body.find_all('td', {'data-stat':'team_game_num'})
                body_AB = body.find_all('td', {'data-stat':'AB'})
                body_H = body.find_all('td', {'data-stat':'H'})
                body_BB = body.find_all('td', {'data-stat':'BB'})
                body_HBP = body.find_all('td', {'data-stat':'HBP'})
                body_2B = body.find_all('td', {'data-stat':'2B'})
                body_3B = body.find_all('td', {'data-stat':'3B'})
                body_HR = body.find_all('td', {'data-stat':'HR'})
                body_RBI = body.find_all('td', {'data-stat':'RBI'})
                body_SO = body.find_all('td', {'data-stat':'SO'})
                body_SF = body.find_all('td', {'data-stat':'SF'})
                body_WPA = body.find_all('td', {'data-stat':'wpa_bat'})
                body_BOP = body.find_all('td', {'data-stat':'batting_order_position'})

                team_id = []
                gtm = []
                days_bw_team_games = []
                atbats = []
                hits = []
                baseonballs = []
                hitbypitch = []
                singles = []
                doubles = []
                triples = []
                homeruns = []
                rbi = []
                strikeouts = []
                sacrifice_f = []
                ba = []
                obp = []
                slg = []
                wpa = []
                batrank = []

                for n in range(len(body_AB)):

                    _team_id = body_TEAMID[n].text
                    _gtm = int(body_GTM[n].text.split('(')[0])

                    if n == 0:
                        _days_bw_team_games = _gtm
                    else:
                        _days_bw_team_games = _gtm - gtm[-1]

                    _ab = int(body_AB[n].text)
                    _h = int(body_H[n].text)
                    _bb = int(body_BB[n].text)
                    _hbp = int(body_HBP[n].text)
                    _2b = int(body_2B[n].text)
                    _3b = int(body_3B[n].text)
                    _hr = int(body_HR[n].text)
                    _rbi = int(body_RBI[n].text)
                    _so = int(body_SO[n].text)
                    _1b = _h - _2b - _3b - _hr
                    _sf = int(body_SF[n].text) if body_SF[n].text != '' else 0
                    try:
                        _wpa = float(body_WPA[n].text)
                    except:
                        _wpa = 0

                    team_id.append(_team_id)
                    gtm.append(_gtm)
                    days_bw_team_games.append(_days_bw_team_games)
                    atbats.append( _ab )
                    hits.append( _h )
                    baseonballs.append( _bb )
                    hitbypitch.append( _hbp)
                    doubles.append( _2b)
                    triples.append( _3b)
                    homeruns.append( _hr)
                    rbi.append(_rbi)
                    strikeouts.append(_so)
                    sacrifice_f.append(_sf)
                    singles.append(_1b)

                    ba.append( (_h / _ab) if _ab > 0 else 0)
                    obp.append(((_h + _bb + _hbp) / (_ab + _bb + _hbp + _sf)) if (_ab + _bb + _hbp + _sf) > 0 else 0 )
                    slg.append(((_1b + 2*_2b + 3*_3b + 4*_hr) / _ab) if _ab > 0 else 0)
                    wpa.append(_wpa)

                for br in body_BOP:

                    batrank.append(br.text)

                team_id_dict = Counter(team_id)

                batrank_dict = Counter(batrank)
                br1  = batrank_dict['1']  if '1'  in batrank_dict.keys() else 0
                br2  = batrank_dict['2']  if '2'  in batrank_dict.keys() else 0
                br3  = batrank_dict['3']  if '3'  in batrank_dict.keys() else 0
                br4  = batrank_dict['4']  if '4'  in batrank_dict.keys() else 0
                br5  = batrank_dict['5']  if '5'  in batrank_dict.keys() else 0
                br6  = batrank_dict['6']  if '6'  in batrank_dict.keys() else 0
                br7  = batrank_dict['7']  if '7'  in batrank_dict.keys() else 0
                br8  = batrank_dict['8']  if '8'  in batrank_dict.keys() else 0
                br9  = batrank_dict['9']  if '9'  in batrank_dict.keys() else 0

                NAME.append(name)
                NAME_KEY.append(namekey)
                YEAR.append(year)
                TEAM.append(team)

                POSITION.append(pos)


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
                BATRANK_MODE.append(_mode(batrank))
                BATRANK_1.append(br1)
                BATRANK_2.append(br2)
                BATRANK_3.append(br3)
                BATRANK_4.append(br4)
                BATRANK_5.append(br5)
                BATRANK_6.append(br6)
                BATRANK_7.append(br7)
                BATRANK_8.append(br8)
                BATRANK_9.append(br9)
                ATBATS.append(sum(atbats))
                ATBATS_MEAN.append(stat.mean(atbats))
                ATBATS_STDEV.append(stat.stdev(atbats) if len(set(atbats)) > 1 else 0)
                HITS.append(sum(hits))
                HITS_MEAN.append(stat.mean(hits))
                HITS_STDEV.append(stat.stdev(hits) if len(set(hits)) > 1 else 0)
                BASESONBALLS.append(sum(baseonballs))
                BASESONBALLS_MEAN.append(stat.mean(baseonballs))
                BASESONBALLS_STDEV.append(stat.stdev(baseonballs) if len(set(baseonballs)) > 1 else 0)
                HITBYPITCH.append(sum(hitbypitch))
                HITBYPITCH_MEAN.append(stat.mean(hitbypitch))
                HITBYPITCH_STDEV.append(stat.stdev(hitbypitch) if len(set(hitbypitch)) > 1 else 0)
                SINGLES.append(sum(singles))
                SINGLES_MEAN.append(stat.mean(singles))
                SINGLES_STDEV.append(stat.stdev(singles) if len(set(singles)) > 1 else 0)
                DOUBLES.append(sum(doubles))
                DOUBLES_MEAN.append(stat.mean(doubles))
                DOUBLES_STDEV.append(stat.stdev(doubles) if len(set(doubles)) > 1 else 0)
                TRIPLES.append(sum(triples))
                TRIPLES_MEAN.append(stat.mean(triples))
                TRIPLES_STDEV.append(stat.stdev(triples) if len(set(triples)) > 1 else 0)
                HOMERUNS.append(sum(homeruns))
                HOMERUNS_MEAN.append(stat.mean(homeruns))
                HOMERUNS_STDEV.append(stat.stdev(homeruns) if len(set(homeruns)) > 1 else 0)
                RBI.append(sum(rbi))
                RBI_MEAN.append(stat.mean(rbi))
                RBI_STDEV.append(stat.stdev(rbi) if len(set(rbi)) > 1 else 0)
                STRIKEOUT.append(sum(strikeouts))
                STRIKEOUT_MEAN.append(stat.mean(strikeouts))
                STRIKEOUT_STDEV.append(stat.stdev(strikeouts) if len(set(strikeouts)) > 1 else 0)
                SACRIFICE_F.append(sum(sacrifice_f))
                BA_MEAN.append(stat.mean(ba))
                BA_STDEV.append(stat.stdev(ba) if len(set(atbats)) > 1 else 0)
                OBP_MEAN.append(stat.mean(obp))
                OBP_STDEV.append(stat.stdev(obp) if len(set(ba)) > 1 else 0)
                SLG_MEAN.append(stat.mean(slg))
                SLG_STDEV.append(stat.stdev(slg) if len(set(slg)) > 1 else 0)
                WPA_MEAN.append(stat.mean(wpa))
                WPA_STDEV.append(stat.stdev(wpa) if len(set(wpa)) > 1 else 0)

                elapsed_ = perf_counter() - start

                hours   = floor(elapsed_ / 60**2)
                minutes = floor((elapsed_ - hours*60**2) / 60)
                seconds = floor(elapsed_ - hours*60**2 -minutes*60)

                print(try_counter, '- success', '- ',team, '- ', year, '- ', name, ' ', pos, ' ', 'Elapsed Time:',  hours, 'hours', minutes, 'minutes', seconds, 'seconds')

            except:

                miss_counter += 1


                misses.write(str(miss_counter) + team + '- ' + year + '- ' + name + ' ' + pos + ' - ' + url_PG + '\n')

                elapsed_ = perf_counter() - start

                hours   = floor(elapsed_ / 60**2)
                minutes = floor((elapsed_ - hours*60**2) / 60)
                seconds = floor(elapsed_ - hours*60**2 -minutes*60)

                print(try_counter, '- miss', '- ',team, '- ', year,'- ', name, ' ',pos, ' ', 'Elapsed Time:',  hours, 'hours', minutes, 'minutes', seconds, 'seconds')

misses.close()





data_dict = {
"NAME": NAME,
"NAME_KEY": NAME_KEY,
"TEAM": TEAM,
"YEAR": YEAR,
"POSITION": POSITION,
"GAMES": GAMES,
"DAYS_BW_TEAM_GAMES_MEAN": DAYS_BW_TEAM_GAMES_MEAN,
"DAYS_BW_TEAM_GAMES_STDEV": DAYS_BW_TEAM_GAMES_STDEV,
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
"BATRANK_MODE": BATRANK_MODE,
"BATRANK_1": BATRANK_1,
"BATRANK_2": BATRANK_2,
"BATRANK_3": BATRANK_3,
"BATRANK_4": BATRANK_4,
"BATRANK_5": BATRANK_5,
"BATRANK_6": BATRANK_6,
"BATRANK_7": BATRANK_7,
"BATRANK_8": BATRANK_8,
"BATRANK_9": BATRANK_9,
"ATBATS": ATBATS,
"ATBATS_MEAN": ATBATS_MEAN,
"ATBATS_STDEV": ATBATS_STDEV,
"HITS": HITS,
"HITS_MEAN": HITS_MEAN,
"HITS_STDEV": HITS_STDEV,
"BASESONBALLS": BASESONBALLS,
"BASESONBALLS_MEAN": BASESONBALLS_MEAN,
"BASESONBALLS_STDEV": BASESONBALLS_STDEV,
"HITBYPITCH": HITBYPITCH,
"HITBYPITCH_MEAN": HITBYPITCH_MEAN,
"HITBYPITCH_STDEV": HITBYPITCH_STDEV,
"SINGLES": SINGLES,
"SINGLES_MEAN": SINGLES_MEAN,
"SINGLES_STDEV": SINGLES_STDEV,
"DOUBLES": DOUBLES,
"DOUBLES_MEAN": DOUBLES_MEAN,
"DOUBLES_STDEV": DOUBLES_STDEV,
"TRIPLES": TRIPLES,
"TRIPLES_MEAN": TRIPLES_MEAN,
"TRIPLES_STDEV": TRIPLES_STDEV,
"HOMERUNS": HOMERUNS,
"HOMERUNS_MEAN": HOMERUNS_MEAN,
"HOMERUNS_STDEV": HOMERUNS_STDEV,
"RBI": RBI,
"RBI_MEAN": RBI_MEAN,
"RBI_STDEV": RBI_STDEV,
"STRIKEOUT": STRIKEOUT,
"STRIKEOUT_MEAN": STRIKEOUT_MEAN,
"STRIKEOUT_STDEV": STRIKEOUT_STDEV,
"SACRIFICE_F": SACRIFICE_F,
"BA_MEAN": BA_MEAN,
"BA_STDEV": BA_STDEV,
"OBP_MEAN": OBP_MEAN,
"OBP_STDEV": OBP_STDEV,
"SLG_MEAN": SLG_MEAN,
"SLG_STDEV": SLG_STDEV,
"WPA_MEAN": WPA_MEAN,
"WPA_STDEV": WPA_STDEV
}

columns =[\
"NAME",\
"NAME_KEY",\
"TEAM",\
"YEAR",\
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
"BATRANK_MODE",\
"BATRANK_1",\
"BATRANK_2",\
"BATRANK_3",\
"BATRANK_4",\
"BATRANK_5",\
"BATRANK_6",\
"BATRANK_7",\
"BATRANK_8",\
"BATRANK_9",\
"ATBATS",\
"ATBATS_MEAN",\
"ATBATS_STDEV",\
"HITS",\
"HITS_MEAN",\
"HITS_STDEV",\
"BASESONBALLS",\
"BASESONBALLS_MEAN",\
"BASESONBALLS_STDEV",\
"HITBYPITCH",\
"HITBYPITCH_MEAN",\
"HITBYPITCH_STDEV",\
"SINGLES",\
"SINGLES_MEAN",\
"SINGLES_STDEV",\
"DOUBLES",\
"DOUBLES_MEAN",\
"DOUBLES_STDEV",\
"TRIPLES",\
"TRIPLES_MEAN",\
"TRIPLES_STDEV",\
"HOMERUNS",\
"HOMERUNS_MEAN",\
"HOMERUNS_STDEV",\
"RBI",\
"RBI_MEAN",\
"RBI_STDEV",\
"STRIKEOUT",\
"STRIKEOUT_MEAN",\
"STRIKEOUT_STDEV",\
"SACRIFICE_F",\
"BA_MEAN",\
"BA_STDEV",\
"OBP_MEAN",\
"OBP_STDEV",\
"SLG_MEAN",\
"SLG_STDEV",\
"WPA_MEAN",\
"WPA_STDEV"]

df = pd.DataFrame(data_dict, columns=columns)
df.to_csv('batting.csv', mode='w', header = True, index = False)
