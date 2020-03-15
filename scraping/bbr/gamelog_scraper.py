"""
Filename: gamelog_scraper.py
Date: 2020/03/14
Description: Script to scrape all gamelogs from bbr over specified period of years and load in to SQLite DB.
"""

import bs4
from datetime import date
import os
import pandas as pd
import requests
import sqlite3
import time


scrape_years = list(reversed(range(2000,2020)))
sqlite_path = '/Users/qlanners/projects/mlb_salary_comp/sqlite_db/mlb_salary_comp.db'
print_out = True
create_logs = True


def passed_time(start):
    sec = time.time() - start
    hr = sec // (60*60)
    sec = sec - (hr*60*60)
    mn = sec // (60)
    sec = sec - (mn*60)
    return f'{int(hr)}:{int(mn)}:{int(sec)}'


def create_db_connection(path):
    try:
        con = sqlite3.connect(path)
    except:
        print('Error connecting to db.')
        exit()
    return con


def scrape_gamelogs(years, db_path, print_progress=False, log_progress=False, log_folder=None):
    url_gamelog = 'https://www.baseball-reference.com/players/gl.fcgi?id=player_id&t=gamelog_type&year=year_num'
    gamelog_types = {'b': 'batting', 'f': 'fielding', 'p': 'pitching'}
    start_time = time.time()
    con = create_db_connection(db_path)
    if log_progress:
        today = date.today().strftime("%Y_%m_%d")
        if not log_folder:
            log_folder = f'{os.getcwd()}/{today}_logs/'
            if not os.path.exists(f'{log_folder}/all_logs/'):
                os.makedirs(f'{log_folder}/all_logs/')
    for year in years:
        if print_progress:
            print(f'Starting {year}{"." * 100}')
        if log_progress:
            error_count = {'Loading URL Table': 0,
                           'Table Index': 0,
                           'Wrong Table': 0,
                           'Editing Table': 0,
                           'DB': 0
                           }
            all_logs = open(f"{log_folder}all_logs/{str(year)}_logs.txt", "w+")
            all_logs.write(f'Starting {year}{"." * 100}\n')
        url_L = f"https://www.baseball-reference.com/leagues/MLB/{year}.shtml"
        res_L = requests.get(url_L)
        soup_L = bs4.BeautifulSoup(res_L.text, 'html.parser')
        body_L = soup_L.find('tbody')
        teams_urls = [link['href'] for link in body_L.findAll('a', href=True)]

        for url_team in teams_urls:
            url_T = 'https://www.baseball-reference.com' + url_team
            res_T = requests.get(url_T)
            soup_T = bs4.BeautifulSoup(res_T.text, 'html.parser')
            batters = [link['href'] for link in
                       soup_T.find('table', {'id': 'team_batting'}).find('tbody').findAll('a', href=True)]
            pitchers = [link['href'] for link in
                        soup_T.find('table', {'id': 'team_pitching'}).find('tbody').findAll('a', href=True)]
            players = set([p.split('.shtml')[0].split('/')[-1] for p in batters + pitchers])
            for p in players:
                if print_progress:
                    print(f'{p}: {year}')
                if log_progress:
                    all_logs.write(f'{p}: {year}\n')
                for k, v in gamelog_types.items():
                    attempts = 0
                    try:
                        while attempts < 3:
                            try:
                                games_table = pd.read_html(requests.get(
                                    url_gamelog.replace('player_id', p).replace('gamelog_type', k).replace('year_num',
                                                                                                           str(year)),
                                    timeout=10).text, header=0)
                                attempts = 99
                            except requests.exceptions.RequestException:
                                attempts += 1
                                if attempts == 3:
                                    raise ValueError
                    except ValueError:
                        if print_progress:
                            print(f'-{k} (Loading URL Table)')
                        if log_progress:
                            all_logs.write(f'-{k} (Loading URL Table)\n')
                            error_count['Loading URL Table'] += 1
                        continue
                    try:
                        if k == 'f':
                            games_table = games_table[0]
                        else:
                            games_table = games_table[-1]
                    except:
                        if print_progress:
                            print(f'-{k} (Table Index)')
                        if log_progress:
                            all_logs.write(f'-{k} (Table Index)\n')
                            error_count['Table Index'] += 1
                        continue
                    if k == 'b':
                        if 'OBP' not in games_table.columns:
                            if print_progress:
                                print(f'-{k} (Wrong Table)')
                            if log_progress:
                                all_logs.write(f'-{k} (Wrong Table)\n')
                                error_count['Wrong Table'] += 1
                            continue
                    elif k == 'f':
                        if 'E' not in games_table.columns:
                            if print_progress:
                                print(f'-{k} (Wrong Table)')
                            if log_progress:
                                all_logs.write(f'-{k} (Wrong Table)\n')
                                error_count['Wrong Table'] += 1
                            continue
                    elif k == 'p':
                        if 'IP' not in games_table.columns:
                            if print_progress:
                                print(f'-{k} (Wrong Table)')
                            if log_progress:
                                all_logs.write(f'-{k} (Wrong Table)\n')
                                error_count['Wrong Table'] += 1
                            continue
                    try:
                        games_table = games_table[games_table['Tm'] != 'Tm']
                        games_table.dropna(subset=['Rk'], inplace=True)
                        games_table.reset_index(inplace=True)
                        games_table.insert(0, 'year', year)
                        games_table.insert(0, 'player_id', p)
                    except KeyError:
                        if print_progress:
                            print(f'-{k} (Editing Table)')
                        if log_progress:
                            all_logs.write(f'-{k} (Editing Table)\n')
                            error_count['Editing Table'] += 1
                        continue
                    try:
                        games_table.to_sql(f'games_{v}', con, if_exists='append', index=False)
                        if print_progress:
                            print(f'.{k}')
                        if log_progress:
                            all_logs.write(f'.{k}\n')
                    except:
                        if print_progress:
                            print(f'-{k} (DB)')
                        if log_progress:
                            all_logs.write(f'-{k} (DB)\n')
                            error_count['DB'] += 1
            if print_progress:
                print(f'Time Elapsed: {passed_time(start_time)}')
            if log_progress:
                all_logs.write(f'Time Elapsed: {passed_time(start_time)}\n')

        if print_progress:
            print(f'Finished {year}')
            print(f'Time Elapsed: {passed_time(start_time)}')
            print("." * 100)
            print()
        if log_progress:
            all_logs.write(f'Finished {year}\n')
            all_logs.write(f'Time Elapsed: {passed_time(start_time)}\n')
            all_logs.write("." * 100)
            all_logs.write('\n\n')
            all_logs.close()
            log_summary = open(f"{log_folder}log_summary.txt", "a+")
            log_summary.write(f'{year}: \nTime Elapsed: {passed_time(start_time)}\n')
            log_summary.write('Errors:\n')
            for k,v in error_count.items():
                log_summary.write(f'\t{k}: {str(v)}\n')
            log_summary.write('Totals:\n')
            for gt in gamelog_types.values():
                log_summary.write(f'\tGames {gt}: '
                                  f'{con.execute(f"SELECT COUNT(*) FROM games_{gt} where year = {year}").fetchone()[0]}'
                                  f'\n')
            log_summary.close()
    con.close()


if __name__ == '__main__':
    scrape_gamelogs(years=scrape_years, db_path=sqlite_path, print_progress=print_out, log_progress=create_logs,
                    log_folder=None)
