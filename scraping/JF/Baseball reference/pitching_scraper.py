import requests
import bs4
from collections import Counter
import statistics as stat
import pandas as pd
from time import perf_counter
from math import floor
'''
The objective of this scraper is
to grab pitching statistics
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

def try_FLOAT_or_zero(x):
    try:
        return float(x)
    except:
        return 0

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
RSLT_W = []
RSLT_L = []
INNG_IN_CG = []
INNG_IN_GS = []
INNG_IN_SHO = []
INNG_IN_1 = []
INNG_IN_2 = []
INNG_IN_3 = []
INNG_IN_4 = []
INNG_IN_5 = []
INNG_IN_6 = []
INNG_IN_7 = []
INNG_IN_8 = []
INNG_IN_9 = []
INNG_IN_OTHER = []
INNG_OUT_CG = []
INNG_OUT_GF = []
INNG_OUT_SHO = []
INNG_OUT_1 = []
INNG_OUT_2 = []
INNG_OUT_3 = []
INNG_OUT_4 = []
INNG_OUT_5 = []
INNG_OUT_6 = []
INNG_OUT_7 = []
INNG_OUT_8 = []
INNG_OUT_9 = []
INNG_OUT_OTHER = []


DAYS_REST_MEAN = []
DAYS_REST_STDEV = []
DAYS_BW_TEAM_GAMES_MEAN = []
DAYS_BW_TEAM_GAMES_STDEV = []
IP_MEAN = []
IP_STDEV = []
H_MEAN = []
H_STDEV = []
R_MEAN = []
R_STDEV = []
ER_MEAN = []
ER_STDEV = []
BB_MEAN = []
BB_STDEV = []
SO_MEAN = []
SO_STDEV = []
HR_MEAN = []
HR_STDEV = []
HBP_MEAN = []
HBP_STDEV = []
EARNED_RUN_AVG = []
EARNED_RUN_AVG_MEAN = []
EARNED_RUN_AVG_STDEV = []
BATTERS_FACED_MEAN = []
BATTERS_FACED_STDEV = []
PITCHES_MEAN = []
PITCHES_STDEV = []
STRIKES_TOTAL_MEAN = []
STRIKES_TOTAL_STDEV = []
STRIKES_LOOKING_MEAN = []
STRIKES_LOOKING_STDEV = []
STRIKES_SWINGING_MEAN = []
STRIKES_SWINGING_STDEV = []
INPLAY_GB_TOTAL_MEAN = []
INPLAY_GB_TOTAL_STDEV = []
INPLAY_FB_TOTAL_MEAN = []
INPLAY_FB_TOTAL_STDEV = []
INPLAY_LD_MEAN = []
INPLAY_LD_STDEV = []
INPLAY_PU_MEAN = []
INPLAY_PU_STDEV = []
INPLAY_UNK_MEAN = []
INPLAY_UNK_STDEV = []
SB_MEAN = []
SB_STDEV = []
CS_MEAN = []
CS_STDEV = []
PICKOFFS_MEAN = []
PICKOFFS_STDEV = []
AB_MEAN = []
AB_STDEV = []
TWO_B_MEAN = []
TWO_B_STDEV = []
THREE_B_MEAN = []
THREE_B_STDEV = []
IBB_MEAN = []
IBB_STDEV = []
GIDP_MEAN = []
GIDP_STDEV = []
SF_MEAN = []
SF_STDEV = []
ROE_MEAN = []
ROE_STDEV = []
LEVERAGE_INDEX_AVG_MEAN = []
LEVERAGE_INDEX_AVG_STDEV = []
WPA_DEF_MEAN = []
WPA_DEF_STDEV = []
RE24_DEF_MEAN = []
RE24_DEF_STDEV = []

miss_counter = 0
try_counter = 0

misses = open('pitching_misses.txt', 'w')

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

                url_PG = "https://www.baseball-reference.com/players/gl.fcgi?id=" + namekey + "&t=p&year=" + year
                res_PG = requests.get(url_PG)
                soup_PG=bs4.BeautifulSoup(res_PG.text, 'html.parser')


                body = soup_PG.find('tbody')
                body_TEAMID = body.find_all('td', {'data-stat':'team_ID'})
                body_GTM = body.find_all('td', {'data-stat':'team_game_num'})
                body_RSLT = body.find_all('td', {'data-stat':'game_result'})
                body_INNGS = body.find_all('td', {'data-stat':'player_game_span'})
                body_DEC = body.find_all('td', {'data-stat':'player_game_result'})
                body_DR = body.find_all('td', {'data-stat':'days_rest'})
                body_IP = body.find_all('td', {'data-stat':'IP'})
                body_H = body.find_all('td', {'data-stat':'H'})
                body_R = body.find_all('td', {'data-stat':'R'})
                body_ER = body.find_all('td', {'data-stat':'ER'})
                body_BB = body.find_all('td', {'data-stat':'BB'})
                body_SO = body.find_all('td', {'data-stat':'SO'})
                body_HR = body.find_all('td', {'data-stat':'HR'})
                body_HBP = body.find_all('td', {'data-stat':'HBP'})
                body_ERA = body.find_all('td', {'data-stat':'earned_run_avg'})
                body_BF = body.find_all('td', {'data-stat':'batters_faced'})
                body_PIT = body.find_all('td', {'data-stat':'pitches'})
                body_STR = body.find_all('td', {'data-stat':'strikes_total'})
                body_STL = body.find_all('td', {'data-stat':'strikes_looking'})
                body_STS = body.find_all('td', {'data-stat':'strikes_swinging'})
                body_GB = body.find_all('td', {'data-stat':'inplay_gb_total'})
                body_FB = body.find_all('td', {'data-stat':'inplay_fb_total'})
                body_LD = body.find_all('td', {'data-stat':'inplay_ld'})
                body_PU = body.find_all('td', {'data-stat':'inplay_pu'})
                body_UNK = body.find_all('td', {'data-stat':'inplay_unk'})
                body_IR = body.find_all('td', {'data-stat':'inherited_runners'})
                body_IS = body.find_all('td', {'data-stat':'inherited_score'})
                body_SB = body.find_all('td', {'data-stat':'SB'})
                body_CS = body.find_all('td', {'data-stat':'CS'})
                body_PO = body.find_all('td', {'data-stat':'pickoffs'})
                body_AB = body.find_all('td', {'data-stat':'AB'})
                body_2B = body.find_all('td', {'data-stat':'2B'})
                body_3B = body.find_all('td', {'data-stat':'3B'})
                body_IBB = body.find_all('td', {'data-stat':'IBB'})
                body_GDP = body.find_all('td', {'data-stat':'GIDP'})
                body_SF = body.find_all('td', {'data-stat':'SF'})
                body_ROE = body.find_all('td', {'data-stat':'ROE'})
                body_ALI = body.find_all('td', {'data-stat':'leverage_index_avg'})
                body_WPA = body.find_all('td', {'data-stat':'wpa_def'})
                body_RE24 = body.find_all('td', {'data-stat':'re24_def'})

                team_id = []
                game_result = []
                gtm = []
                player_game_inning_in = []
                player_game_inning_out = []
                player_game_result = []
                days_rest = []
                days_bw_team_games = []
                ip = []
                h = []
                r = []
                er = []
                bb = []
                so = []
                hr = []
                hbp = []
                earned_run_avg = []
                era_per_game = []
                batters_faced = []
                pitches = []
                pitches_url = []
                strikes_total = []
                strikes_looking = []
                strikes_swinging = []
                inplay_gb_total = []
                inplay_fb_total = []
                inplay_ld = []
                inplay_pu = []
                inplay_unk = []
                sb = []
                cs = []
                pickoffs = []
                ab = []
                two_b = []
                three_b = []
                ibb = []
                gidp = []
                sf = []
                roe = []
                leverage_index_avg = []
                wpa_def = []
                re24_def = []
                pitcher_situation_in = []
                pitcher_situation_out = []

                for n in range(len(body_RSLT)):

                    _team_id = body_TEAMID[n].text
                    _gtm = try_INT_or_zero(body_GTM[n].text)
                    _game_result = body_RSLT[n].text[0]
                    _player_game_inning_in = body_INNGS[n].text.split('-')[0]
                    _player_game_inning_out = body_INNGS[n].text.split('-')[-1]
                    _player_game_result = body_DEC[n].text.split('(')[0]
                    _days_rest = try_INT_or_zero(body_DR[n].text)

                    if n == 0:
                        _days_bw_team_games = _gtm
                    else:
                        _days_bw_team_games = _gtm - gtm[-1]


                    _ip = try_FLOAT_or_zero(body_IP[n].text)
                    _h = try_INT_or_zero(body_H[n].text)
                    _r = try_INT_or_zero(body_R[n].text)
                    _er = try_INT_or_zero(body_ER[n].text)
                    _bb = try_INT_or_zero(body_BB[n].text)
                    _so = try_INT_or_zero(body_SO[n].text)
                    _hr = try_INT_or_zero(body_HR[n].text)
                    _hbp = try_INT_or_zero(body_HBP[n].text)
                    try:
                        _earned_run_avg = try_FLOAT_or_zero(body_ERA[n].text)
                    except:
                        _earned_run_avg = 0

                    _batters_faced = try_INT_or_zero(body_BF[n].text)
                    _pitches = try_INT_or_zero(body_PIT[n].text)
                    #_pitches_url = body_PIT[n].find('a', href=True)['href']
                    _strikes_total = try_INT_or_zero(body_STR[n].text)
                    _strikes_looking = try_INT_or_zero(body_STL[n].text)
                    _strikes_swinging = try_INT_or_zero(body_STS[n].text)
                    _inplay_gb_total = try_INT_or_zero(body_GB[n].text)
                    _inplay_fb_total = try_INT_or_zero(body_FB[n].text)
                    _inplay_ld = try_INT_or_zero(body_LD[n].text)
                    _inplay_pu = try_INT_or_zero(body_PU[n].text)
                    _inplay_unk = try_INT_or_zero(body_UNK[n].text)
                    _sb = try_INT_or_zero(body_SB[n].text)
                    _cs = try_INT_or_zero(body_CS[n].text)
                    _pickoffs = try_INT_or_zero(body_PO[n].text)
                    _ab = try_INT_or_zero(body_AB[n].text)
                    _two_b = try_INT_or_zero(body_2B[n].text)
                    _three_b = try_INT_or_zero(body_3B[n].text)
                    _ibb = try_INT_or_zero(body_IBB[n].text)
                    _gidp = try_INT_or_zero(body_GDP[n].text)
                    _sf = try_INT_or_zero(body_SF[n].text)
                    _roe = try_INT_or_zero(body_ROE[n].text)
                    _leverage_index_avg = try_FLOAT_or_zero(body_ALI[n].text)
                    _wpa_def = try_FLOAT_or_zero(body_WPA[n].text)
                    _re24_def = try_FLOAT_or_zero(body_RE24[n].text)

                    team_id.append(_team_id)
                    gtm.append(_gtm)
                    game_result.append(_game_result)
                    player_game_inning_in.append(_player_game_inning_in)
                    player_game_inning_out.append(_player_game_inning_out)
                    days_rest.append(_days_rest)
                    days_bw_team_games.append(_days_bw_team_games)
                    ip.append(_ip)
                    h.append(_h)
                    r.append(_r)
                    er.append(_er)
                    bb.append(_bb)
                    so.append(_so)
                    hr.append(_hr)
                    hbp.append(_hbp)
                    earned_run_avg.append(_earned_run_avg)
                    batters_faced.append(_batters_faced)
                    pitches.append(_pitches)
                    #pitches_url.append(_pitches_url)
                    strikes_total.append(_strikes_total)
                    strikes_looking.append(_strikes_looking)
                    strikes_swinging.append(_strikes_swinging)
                    inplay_gb_total.append(_inplay_gb_total)
                    inplay_fb_total.append(_inplay_fb_total)
                    inplay_ld.append(_inplay_ld)
                    inplay_pu.append(_inplay_pu)
                    inplay_unk.append(_inplay_unk)
                    sb.append(_sb)
                    cs.append(_cs)
                    pickoffs.append(_pickoffs)
                    ab.append(_ab)
                    two_b.append(_two_b)
                    three_b.append(_three_b)
                    ibb.append(_ibb)
                    gidp.append(_gidp)
                    sf.append(_sf)
                    roe.append(_roe)
                    leverage_index_avg.append(_leverage_index_avg)
                    wpa_def.append(_wpa_def)
                    re24_def.append(_re24_def)

                team_id_dict = Counter(team_id)


                rslt_dict = Counter(game_result)
                rslt_W  = rslt_dict['W']  if 'W'  in rslt_dict.keys() else 0
                rslt_L  = rslt_dict['L']  if 'L'  in rslt_dict.keys() else 0

                inng_in = Counter(player_game_inning_in)
                inng_in_CG = inng_in['CG']  if 'CG'  in inng_in.keys() else 0
                inng_in_GS = inng_in['GS']  if 'GS'  in inng_in.keys() else 0
                inng_in_SHO = inng_in['SHO']  if 'SHO'  in inng_in.keys() else 0
                inng_in_1 = inng_in['1']  if '1'  in inng_in.keys() else 0
                inng_in_2 = inng_in['2']  if '2'  in inng_in.keys() else 0
                inng_in_3 = inng_in['3']  if '3'  in inng_in.keys() else 0
                inng_in_4 = inng_in['4']  if '4'  in inng_in.keys() else 0
                inng_in_5 = inng_in['5']  if '5'  in inng_in.keys() else 0
                inng_in_6 = inng_in['6']  if '6'  in inng_in.keys() else 0
                inng_in_7 = inng_in['7']  if '7'  in inng_in.keys() else 0
                inng_in_8 = inng_in['8']  if '8'  in inng_in.keys() else 0
                inng_in_9 = inng_in['9']  if '9'  in inng_in.keys() else 0
                inng_in_OTHER = 0
                for k in inng_in.keys():
                    if k not in ('CG','GS','1','2','3','4','5','6','7','8','9','SHO'):
                        inng_in_OTHER += inng_in[k]


                inng_out = Counter(player_game_inning_out)
                inng_out_CG = inng_out['CG']  if 'CG'  in inng_out.keys() else 0
                inng_out_SHO = inng_out['SHO']  if 'SHO'  in inng_out.keys() else 0
                inng_out_1 = inng_out['1']  if '1'  in inng_out.keys() else 0
                inng_out_2 = inng_out['2']  if '2'  in inng_out.keys() else 0
                inng_out_3 = inng_out['3']  if '3'  in inng_out.keys() else 0
                inng_out_4 = inng_out['4']  if '4'  in inng_out.keys() else 0
                inng_out_5 = inng_out['5']  if '5'  in inng_out.keys() else 0
                inng_out_6 = inng_out['6']  if '6'  in inng_out.keys() else 0
                inng_out_7 = inng_out['7']  if '7'  in inng_out.keys() else 0
                inng_out_8 = inng_out['8']  if '8'  in inng_out.keys() else 0
                inng_out_9 = inng_out['9']  if '9'  in inng_out.keys() else 0
                inng_out_GF = inng_out['GF']  if 'GF'  in inng_out.keys() else 0
                inng_out_OTHER = 0
                for k in inng_out.keys():
                    if k not in ('CG','GF','1','2','3','4','5','6','7','8','9', 'SHO'):
                        inng_out_OTHER += inng_out[k]

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

                GAMES.append(len(body_RSLT))


                RSLT_W.append(rslt_W)
                RSLT_L.append(rslt_L)
                INNG_IN_CG.append(inng_in_CG)
                INNG_IN_GS.append(inng_in_GS)
                INNG_IN_SHO.append(inng_in_SHO)
                INNG_IN_1.append(inng_in_1)
                INNG_IN_2.append(inng_in_2)
                INNG_IN_3.append(inng_in_3)
                INNG_IN_4.append(inng_in_4)
                INNG_IN_5.append(inng_in_5)
                INNG_IN_6.append(inng_in_6)
                INNG_IN_7.append(inng_in_7)
                INNG_IN_8.append(inng_in_8)
                INNG_IN_9.append(inng_in_9)
                INNG_IN_OTHER.append(inng_in_OTHER)
                INNG_OUT_CG.append(inng_out_CG)
                INNG_OUT_GF.append(inng_out_GF)
                INNG_OUT_SHO.append(inng_out_SHO)
                INNG_OUT_1.append(inng_out_1)
                INNG_OUT_2.append(inng_out_2)
                INNG_OUT_3.append(inng_out_3)
                INNG_OUT_4.append(inng_out_4)
                INNG_OUT_5.append(inng_out_5)
                INNG_OUT_6.append(inng_out_6)
                INNG_OUT_7.append(inng_out_7)
                INNG_OUT_8.append(inng_out_8)
                INNG_OUT_9.append(inng_out_9)
                INNG_OUT_OTHER.append(inng_out_OTHER)


                DAYS_REST_MEAN.append(stat.mean(days_rest))
                DAYS_REST_STDEV.append(stat.stdev(days_rest)  if len(set(days_rest)) > 1 else 0)
                DAYS_BW_TEAM_GAMES_MEAN.append(stat.mean(days_bw_team_games))
                DAYS_BW_TEAM_GAMES_STDEV.append(stat.stdev(days_bw_team_games)  if len(set(days_bw_team_games)) > 1 else 0)
                IP_MEAN.append(stat.mean(ip))
                IP_STDEV.append(stat.stdev(ip)  if len(set(ip)) > 1 else 0)
                H_MEAN.append(stat.mean(h))
                H_STDEV.append(stat.stdev(h)  if len(set(h)) > 1 else 0)
                R_MEAN.append(stat.mean(r))
                R_STDEV.append(stat.stdev(r)  if len(set(r)) > 1 else 0)
                ER_MEAN.append(stat.mean(er))
                ER_STDEV.append(stat.stdev(er)  if len(set(er)) > 1 else 0)
                BB_MEAN.append(stat.mean(bb))
                BB_STDEV.append(stat.stdev(bb)  if len(set(bb)) > 1 else 0)
                SO_MEAN.append(stat.mean(so))
                SO_STDEV.append(stat.stdev(so)  if len(set(so)) > 1 else 0)
                HR_MEAN.append(stat.mean(hr))
                HR_STDEV.append(stat.stdev(hr)  if len(set(hr)) > 1 else 0)
                HBP_MEAN.append(stat.mean(hbp))
                HBP_STDEV.append(stat.stdev(hbp)  if len(set(hbp)) > 1 else 0)
                EARNED_RUN_AVG.append(earned_run_avg[-1])
                EARNED_RUN_AVG_MEAN.append(stat.mean(earned_run_avg))
                EARNED_RUN_AVG_STDEV.append(stat.stdev(earned_run_avg)  if len(set(earned_run_avg)) > 1 else 0)
                BATTERS_FACED_MEAN.append(stat.mean(batters_faced))
                BATTERS_FACED_STDEV.append(stat.stdev(batters_faced)  if len(set(batters_faced)) > 1 else 0)
                PITCHES_MEAN.append(stat.mean(pitches))
                PITCHES_STDEV.append(stat.stdev(pitches)  if len(set(pitches)) > 1 else 0)
                STRIKES_TOTAL_MEAN.append(stat.mean(strikes_total))
                STRIKES_TOTAL_STDEV.append(stat.stdev(strikes_total)  if len(set(strikes_total)) > 1 else 0)
                STRIKES_LOOKING_MEAN.append(stat.mean(strikes_looking))
                STRIKES_LOOKING_STDEV.append(stat.stdev(strikes_looking)  if len(set(strikes_looking)) > 1 else 0)
                STRIKES_SWINGING_MEAN.append(stat.mean(strikes_swinging))
                STRIKES_SWINGING_STDEV.append(stat.stdev(strikes_swinging)  if len(set(strikes_swinging)) > 1 else 0)
                INPLAY_GB_TOTAL_MEAN.append(stat.mean(inplay_gb_total))
                INPLAY_GB_TOTAL_STDEV.append(stat.stdev(inplay_gb_total)  if len(set(inplay_gb_total)) > 1 else 0)
                INPLAY_FB_TOTAL_MEAN.append(stat.mean(inplay_fb_total))
                INPLAY_FB_TOTAL_STDEV.append(stat.stdev(inplay_fb_total)  if len(set(inplay_fb_total)) > 1 else 0)
                INPLAY_LD_MEAN.append(stat.mean(inplay_ld))
                INPLAY_LD_STDEV.append(stat.stdev(inplay_ld)  if len(set(inplay_ld)) > 1 else 0)
                INPLAY_PU_MEAN.append(stat.mean(inplay_pu))
                INPLAY_PU_STDEV.append(stat.stdev(inplay_pu)  if len(set(inplay_pu)) > 1 else 0)
                INPLAY_UNK_MEAN.append(stat.mean(inplay_unk))
                INPLAY_UNK_STDEV.append(stat.stdev(inplay_unk)  if len(set(inplay_unk)) > 1 else 0)
                SB_MEAN.append(stat.mean(sb))
                SB_STDEV.append(stat.stdev(sb)  if len(set(sb)) > 1 else 0)
                CS_MEAN.append(stat.mean(cs))
                CS_STDEV.append(stat.stdev(cs)  if len(set(cs)) > 1 else 0)
                PICKOFFS_MEAN.append(stat.mean(pickoffs))
                PICKOFFS_STDEV.append(stat.stdev(pickoffs)  if len(set(pickoffs)) > 1 else 0)
                AB_MEAN.append(stat.mean(ab))
                AB_STDEV.append(stat.stdev(ab)  if len(set(ab)) > 1 else 0)
                TWO_B_MEAN.append(stat.mean(two_b))
                TWO_B_STDEV.append(stat.stdev(two_b)  if len(set(two_b)) > 1 else 0)
                THREE_B_MEAN.append(stat.mean(three_b))
                THREE_B_STDEV.append(stat.stdev(three_b)  if len(set(three_b)) > 1 else 0)
                IBB_MEAN.append(stat.mean(ibb))
                IBB_STDEV.append(stat.stdev(ibb)  if len(set(ibb)) > 1 else 0)
                GIDP_MEAN.append(stat.mean(gidp))
                GIDP_STDEV.append(stat.stdev(gidp)  if len(set(gidp)) > 1 else 0)
                SF_MEAN.append(stat.mean(sf))
                SF_STDEV.append(stat.stdev(sf)  if len(set(sf)) > 1 else 0)
                ROE_MEAN.append(stat.mean(roe))
                ROE_STDEV.append(stat.stdev(roe)  if len(set(roe)) > 1 else 0)
                LEVERAGE_INDEX_AVG_MEAN.append(stat.mean(leverage_index_avg))
                LEVERAGE_INDEX_AVG_STDEV.append(stat.stdev(leverage_index_avg)  if len(set(leverage_index_avg)) > 1 else 0)
                WPA_DEF_MEAN.append(stat.mean(wpa_def))
                WPA_DEF_STDEV.append(stat.stdev(wpa_def)  if len(set(wpa_def)) > 1 else 0)
                RE24_DEF_MEAN.append(stat.mean(re24_def))
                RE24_DEF_STDEV.append(stat.stdev(re24_def)  if len(set(re24_def)) > 1 else 0)


                elapsed_ = perf_counter() - start

                hours   = floor(elapsed_ / 60**2)
                minutes = floor((elapsed_ - hours*60**2) / 60)
                seconds = floor(elapsed_ - hours*60**2 -minutes*60)

                print(try_counter, '- success', '- ',team, '- ', year, '- ', name, ' ', pos, ' ', 'Elapsed Time:',  hours, 'hours', minutes, 'minutes', seconds, 'seconds')

            except:

                miss_counter += 1

                if pos == 'P':
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
"DAYS_REST_MEAN": DAYS_REST_MEAN,
"DAYS_REST_STDEV": DAYS_REST_STDEV,
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
"RSLT_W": RSLT_W,
"RSLT_L": RSLT_L,
"INNG_IN_CG": INNG_IN_CG,
"INNG_IN_GS": INNG_IN_GS,
"INNG_IN_SHO": INNG_IN_SHO,
"INNG_IN_1": INNG_IN_1,
"INNG_IN_2": INNG_IN_2,
"INNG_IN_3": INNG_IN_3,
"INNG_IN_4": INNG_IN_4,
"INNG_IN_5": INNG_IN_5,
"INNG_IN_6": INNG_IN_6,
"INNG_IN_7": INNG_IN_7,
"INNG_IN_8": INNG_IN_8,
"INNG_IN_9": INNG_IN_9,
"INNG_IN_OTHER": INNG_IN_OTHER,
"INNG_OUT_CG": INNG_OUT_CG,
"INNG_OUT_SHO": INNG_OUT_SHO,
"INNG_OUT_1": INNG_OUT_1,
"INNG_OUT_2": INNG_OUT_2,
"INNG_OUT_3": INNG_OUT_3,
"INNG_OUT_4": INNG_OUT_4,
"INNG_OUT_5": INNG_OUT_5,
"INNG_OUT_6": INNG_OUT_6,
"INNG_OUT_7": INNG_OUT_7,
"INNG_OUT_8": INNG_OUT_8,
"INNG_OUT_9": INNG_OUT_9,
"INNG_OUT_GF": INNG_OUT_GF,
"INNG_OUT_OTHER": INNG_OUT_OTHER,
"IP_MEAN": IP_MEAN,
"IP_STDEV": IP_STDEV,
"H_MEAN": H_MEAN,
"H_STDEV": H_STDEV,
"R_MEAN": R_MEAN,
"R_STDEV": R_STDEV,
"ER_MEAN": ER_MEAN,
"ER_STDEV": ER_STDEV,
"BB_MEAN": BB_MEAN,
"BB_STDEV": BB_STDEV,
"SO_MEAN": SO_MEAN,
"SO_STDEV": SO_STDEV,
"HR_MEAN": HR_MEAN,
"HR_STDEV": HR_STDEV,
"HBP_MEAN": HBP_MEAN,
"HBP_STDEV": HBP_STDEV,
"EARNED_RUN_AVG": EARNED_RUN_AVG,
"EARNED_RUN_AVG_MEAN": EARNED_RUN_AVG_MEAN,
"EARNED_RUN_AVG_STDEV": EARNED_RUN_AVG_STDEV,
"BATTERS_FACED_MEAN": BATTERS_FACED_MEAN,
"BATTERS_FACED_STDEV": BATTERS_FACED_STDEV,
"PITCHES_MEAN": PITCHES_MEAN,
"PITCHES_STDEV": PITCHES_STDEV,
"STRIKES_TOTAL_MEAN": STRIKES_TOTAL_MEAN,
"STRIKES_TOTAL_STDEV": STRIKES_TOTAL_STDEV,
"STRIKES_LOOKING_MEAN": STRIKES_LOOKING_MEAN,
"STRIKES_LOOKING_STDEV": STRIKES_LOOKING_STDEV,
"STRIKES_SWINGING_MEAN": STRIKES_SWINGING_MEAN,
"STRIKES_SWINGING_STDEV": STRIKES_SWINGING_STDEV,
"INPLAY_GB_TOTAL_MEAN": INPLAY_GB_TOTAL_MEAN,
"INPLAY_GB_TOTAL_STDEV": INPLAY_GB_TOTAL_STDEV,
"INPLAY_FB_TOTAL_MEAN": INPLAY_FB_TOTAL_MEAN,
"INPLAY_FB_TOTAL_STDEV": INPLAY_FB_TOTAL_STDEV,
"INPLAY_LD_MEAN": INPLAY_LD_MEAN,
"INPLAY_LD_STDEV": INPLAY_LD_STDEV,
"INPLAY_PU_MEAN": INPLAY_PU_MEAN,
"INPLAY_PU_STDEV": INPLAY_PU_STDEV,
"INPLAY_UNK_MEAN": INPLAY_UNK_MEAN,
"INPLAY_UNK_STDEV": INPLAY_UNK_STDEV,
"SB_MEAN": SB_MEAN,
"SB_STDEV": SB_STDEV,
"CS_MEAN": CS_MEAN,
"CS_STDEV": CS_STDEV,
"PICKOFFS_MEAN": PICKOFFS_MEAN,
"PICKOFFS_STDEV": PICKOFFS_STDEV,
"AB_MEAN": AB_MEAN,
"AB_STDEV": AB_STDEV,
"TWO_B_MEAN": TWO_B_MEAN,
"TWO_B_STDEV": TWO_B_STDEV,
"THREE_B_MEAN": THREE_B_MEAN,
"THREE_B_STDEV": THREE_B_STDEV,
"IBB_MEAN": IBB_MEAN,
"IBB_STDEV": IBB_STDEV,
"GIDP_MEAN": GIDP_MEAN,
"GIDP_STDEV": GIDP_STDEV,
"SF_MEAN": SF_MEAN,
"SF_STDEV": SF_STDEV,
"ROE_MEAN": ROE_MEAN,
"ROE_STDEV": ROE_STDEV,
"LEVERAGE_INDEX_AVG_MEAN": LEVERAGE_INDEX_AVG_MEAN,
"LEVERAGE_INDEX_AVG_STDEV": LEVERAGE_INDEX_AVG_STDEV,
"WPA_DEF_MEAN": WPA_DEF_MEAN,
"WPA_DEF_STDEV": WPA_DEF_STDEV,
"RE24_DEF_MEAN": RE24_DEF_MEAN,
"RE24_DEF_STDEV": RE24_DEF_STDEV
}

columns =[\
'NAME',\
"NAME_KEY",\
"TEAM",\
"YEAR",\
"POSITION",\
"GAMES",\
"DAYS_REST_MEAN",\
"DAYS_REST_STDEV",\
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
"RSLT_W",\
"RSLT_L",\
"INNG_IN_CG",\
"INNG_IN_GS",\
"INNG_IN_SHO",\
"INNG_IN_1",\
"INNG_IN_2",\
"INNG_IN_3",\
"INNG_IN_4",\
"INNG_IN_5",\
"INNG_IN_6",\
"INNG_IN_7",\
"INNG_IN_8",\
"INNG_IN_9",\
"INNG_IN_OTHER",\
"INNG_OUT_CG",\
"INNG_OUT_SHO",\
"INNG_OUT_1",\
"INNG_OUT_2",\
"INNG_OUT_3",\
"INNG_OUT_4",\
"INNG_OUT_5",\
"INNG_OUT_6",\
"INNG_OUT_7",\
"INNG_OUT_8",\
"INNG_OUT_9",\
"INNG_OUT_GF",\
"INNG_OUT_OTHER",\
"IP_MEAN",\
"IP_STDEV",\
"H_MEAN",\
"H_STDEV",\
"R_MEAN",\
"R_STDEV",\
"ER_MEAN",\
"ER_STDEV",\
"BB_MEAN",\
"BB_STDEV",\
"SO_MEAN",\
"SO_STDEV",\
"HR_MEAN",\
"HR_STDEV",\
"HBP_MEAN",\
"HBP_STDEV",\
"EARNED_RUN_AVG",\
"EARNED_RUN_AVG_MEAN",\
"EARNED_RUN_AVG_STDEV",\
"BATTERS_FACED_MEAN",\
"BATTERS_FACED_STDEV",\
"PITCHES_MEAN",\
"PITCHES_STDEV",\
"STRIKES_TOTAL_MEAN",\
"STRIKES_TOTAL_STDEV",\
"STRIKES_LOOKING_MEAN",\
"STRIKES_LOOKING_STDEV",\
"STRIKES_SWINGING_MEAN",\
"STRIKES_SWINGING_STDEV",\
"INPLAY_GB_TOTAL_MEAN",\
"INPLAY_GB_TOTAL_STDEV",\
"INPLAY_FB_TOTAL_MEAN",\
"INPLAY_FB_TOTAL_STDEV",\
"INPLAY_LD_MEAN",\
"INPLAY_LD_STDEV",\
"INPLAY_PU_MEAN",\
"INPLAY_PU_STDEV",\
"INPLAY_UNK_MEAN",\
"INPLAY_UNK_STDEV",\
"SB_MEAN",\
"SB_STDEV",\
"CS_MEAN",\
"CS_STDEV",\
"PICKOFFS_MEAN",\
"PICKOFFS_STDEV",\
"AB_MEAN",\
"AB_STDEV",\
"TWO_B_MEAN",\
"TWO_B_STDEV",\
"THREE_B_MEAN",\
"THREE_B_STDEV",\
"IBB_MEAN",\
"IBB_STDEV",\
"GIDP_MEAN",\
"GIDP_STDEV",\
"SF_MEAN",\
"SF_STDEV",\
"ROE_MEAN",\
"ROE_STDEV",\
"LEVERAGE_INDEX_AVG_MEAN",\
"LEVERAGE_INDEX_AVG_STDEV",\
"WPA_DEF_MEAN",\
"WPA_DEF_STDEV",\
"RE24_DEF_MEAN",\
"RE24_DEF_STDEV"]

for i in data_dict.keys():
    print(str(i), len(data_dict[i]))


df = pd.DataFrame(data_dict, columns=columns)
df.to_csv('pitching.csv', mode='w', header = True, index = False)
