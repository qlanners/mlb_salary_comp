"""
file name: salary_scraper.py
date created: 1/18/19
last edited: 1/25/19
created by: Quinn Lanners
description: python script that creates two csv files to which it appends player information to the first and corresponding salary data 
            scraped from www.Spotrac.com to the second. Data can be scraped back as far as desired, however Spotrac only goes so far.
            The salary data scraped is from players in both the Active Roster and Disabled List tables from Spotrac. Player keys are created
            for each player using the Spotrac key for that player. Furthermore, if specified, this script also produces two additional csv 
            files alongside the two master csv files: the two additioanl files split the salaries by position, creatng one file for 
            batters/position players salaries and one for pitchers salaries.
"""


"""
import all packages. 
    -Selenium used to scrape data from web using an instance of Chrome in the background.
    -BeautifulSoup used to extract text from HTML
    -pandas used for dataframe
    -split_salaries is used to split salary data into seperate files for batters and pitchers (see split_salaries.py)
"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
from bs4 import BeautifulSoup
from split_salaries import split_salaries
import re
import math

#output csv names
players_csv = 'players.csv'
salaries_csv = 'salaries.csv'
batter_salaries_csv = 'batters.csv'
pitcher_salaries_csv = 'pitchers.csv'

#list of the years from which to scrape salary data from
years = list(range(2000,2020))

#Dictionary of team abbreviations and corresponding url component used by spotrac for that team. Used to create unique URLs for each team
teams = {
    'LAA':'los-angeles-angels',
    'CHW':'chicago-white-sox',
    'CLE':'cleveland-indians',
    'KC':'kansas-city-royals',
    'MIL':'milwaukee-brewers',
    'OAK':'oakland-athletics',
    'SEA':'seattle-mariners',
    'TEX':'texas-rangers',
    'CHC':'chicago-cubs',
    'CIN':'cincinnati-reds',
    'LAD':'los-angeles-dodgers',
    'SD':'san-diego-padres',
    'SF':'san-francisco-giants',
    'COL':'colorado-rockies',
    'ARI':'arizona-diamondbacks',
    'BAL':'baltimore-orioles',
    'BOS':'boston-red-sox',
    'DET':'detroit-tigers',
    'MIN':'minnesota-twins',
    'NYY':'new-york-yankees',
    'TOR':'toronto-blue-jays',
    'ATL':'atlanta-braves',
    'HOU':'houston-astros',
    'WSH':'washington-nationals',
    'NYM':'new-york-mets',
    'PHI':'philadelphia-phillies',
    'PIT':'pittsburgh-pirates',
    'STL':'st.-louis-cardinals',
    'MIA':'miami-marlins',
    'TB':'tampa-bay-rays'
}

def as_hours(s):
    """Take time in seconds as input and returns of string of hours minutes and seconds"""
    m = math.floor(s / 60)
    h = math.floor(m / 60)
    s -= m * 60
    m -= h * 60
    return '%dh %dm %ds' % (h, m, s)


def remove_duplicate(name):
    """Remove duplcate name to clean scraped data from spotrac

    this function was created to deal with a strange error that occurs when scraping from Spotrac. The error is that every player's name
    is repeated twice in the name column. This function in turn returns once instance of their last name in the form of a list
    which is then joined together to produce one name in the format 'Last_Name First_Name'
    args:
        name: a list of a name split using the split() function in python
    returns:
        shortened_name: a list which removed all duplicate words

    """
    shortened_name = []
    [shortened_name.append(x) for x in name if x not in shortened_name]
    return shortened_name

def create_empty_csv(csv_path, col_names):
    """Creates a new, empty, csv file with nothing other than column headers."""
    df = pd.DataFrame(columns=col_names)
    df.to_csv(csv_path, encoding='utf-8', index=False)


def drop_duplicated(csv_path):
    """Delete duplicate rows from a csv by converting it into a pandas dataframe and then back into a csv"""
    df = pd.read_csv(csv_path)
    df.drop_duplicates(subset='key', inplace=True)
    df.to_csv(csv_path)    


def salary_scraper(team, team_url, year, players_csv_path, salaries_csv_path):
    """Scrape salaries for a team for a given year

    This function scrapes salary data for a specified team for a specified year and appends the player data to the speciied player_csv 
    and the salary data to the specified salary_csv. Salary data is scraped for both active and disabled list players. 
    The function appends data to the csv and prints '.' if succesful, else the function prints a message indicating the failure to do so.   
    args:
        team: string of the abbrevation for a team (ex. Minnesota Twins = MIN)
        team_url: string of the unique portion of the spotrac url for the desired team. For example, Minnesota Twins, is minnesota-twins
        year: string/int value for the desired year
        players_csv_path: string of the path to the csv to which the player information is to be appended to
        salaries_csv_path: string of the path to the csv to which the salary information is to be appended to
    """
    try:
        option = Options()
        option.add_argument(" - incognito")
        option.add_argument("--no-startup-window")
        option.add_argument("--headless")

        capa = DesiredCapabilities.CHROME
        capa["pageLoadStrategy"] = "none"

        
        '''ensure that the executable_path points to the directory where your chromedriver is installed (note this code is optimized for 
        google cloud services and thus the path will be different if being run on local computer)'''
        driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options = option, desired_capabilities = capa)

        #have the chromedriver wait 5 seconds if page isn't instantly located
        wait = WebDriverWait(driver, 30)

        #create the unique url for the payroll site for the team and year
        url = "https://www.spotrac.com/mlb/"+team_url+"/payroll/"+str(year)+"/"
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main']/div[4]/table[1]")))

        #get the active players salary table
        active = driver.find_element_by_xpath("//*[@id='main']/div[4]/table[1]").get_attribute('outerHTML')

        #get the title of the second salary table
        table_two_title = BeautifulSoup(driver.find_element_by_xpath("//*[@id='main']/div[4]/header[1]/h2").get_attribute('outerHTML'), "lxml").get_text()

        #if the second table on the page is for players on the disabled list, get table, else don't get table
        if 'Disabled' in table_two_title:
            disabled = driver.find_element_by_xpath("//*[@id='main']/div[4]/table[2]").get_attribute('outerHTML')

        driver.execute_script("window.stop();")
        driver.stop_client()
        driver.close()

        #get Spotrac player URL link for each player in the scraped tables
        player_links = []
        active_soup = BeautifulSoup(active, "lxml")
        for link in active_soup.findAll('a'):
            player_links.append(link.get('href'))

        #read active players into pandas dataframe
        active = pd.read_html(active)
        active = active[0]
        active['type'] = 'A'

        #if second table is disabled players, append these players to the salaries pandas dataframe
        if 'Disabled' in table_two_title:
            disabled_soup = BeautifulSoup(disabled, "lxml")
            for link in disabled_soup.findAll('a'):
                player_links.append(link.get('href'))
            disabled = pd.read_html(disabled)
            disabled = disabled[0]
            disabled['type'] = 'D'
            for index, row in disabled.iterrows():
                if '7' in disabled.iloc[index,0]:
                    disabled.iloc[index,0] = disabled.iloc[index,0][:-8]
                elif '(' in disabled.iloc[index,0]:
                    disabled.iloc[index,0] = disabled.iloc[index,0][:-9]
            disabled.columns = list(active)
            all_salaries = pd.concat([active,disabled], ignore_index=True)
        
        else:
            all_salaries = active
        
        all_salaries['year'] = year
        all_salaries['team'] = team
        player_name_row = list(active)[0]

        #use the remove duplicate functions to deal with Spotrac issue of duplicating players names when scraping
        for index, row in all_salaries.iterrows():
            all_salaries.at[index,player_name_row] = ' '.join(remove_duplicate(row[player_name_row].split()))

        #get Spotrac player keys from the scraped Spotrac URL for each player
        spotrac_keys = []
        for link in player_links:
            spotrac_keys.append(re.search('player/(.+?)/', link).group(1))
        all_salaries['spotrac_key'] = spotrac_keys

        #create a dataframe for player information
        all_players = all_salaries[['spotrac_key',player_name_row,'Pos.']]
        all_players['spotrac_link'] = player_links
        
        #drop player information from salaries dataframe
        all_salaries.drop(player_name_row, axis=1, inplace=True)
        all_salaries.drop('Pos.', axis=1, inplace=True)

        #append the table to the specified csvs
        with open(players_csv_path, 'a') as players:
            all_players.to_csv(players, encoding='utf-8', index=False, header=False)
        with open(salaries_csv_path, 'a') as salaries:
            all_salaries.to_csv(salaries, encoding='utf-8', index=False, header=False)

        print('.')

    #print a failure message if the data for this team in this year cannot be retrieved
    except:
        print('Failure for '+team+' '+str(year))


def main(players_csv_path, salaries_csv_path, years, teams, split=True, batter_salaries_path='salaries_batters.csv', pitcher_salaries_path='salaries_pitchers.csv'):
    """Main function to scrape player salary data from spotrac

    This function combines all of the previous functions into a master script, which scrapes data for the specified MLB teams over the specified years
    from Spotrac.com, and then creates 2 csv files in the working directory with the given names. Furthermore, this function has the option to
    create two additional csv files: one for all of the batter salary info and one for all of the pitcher salary info   
    args:
        players_csv_path: string value of the name of the new csv file to be created which will contain player information for both batters and pitchers
                  for all specified MLB teams over the specified years
        salaries_csv_path: string value of the name of the new csv file to be created which will contain salary information for both batters and pitchers
                  for all specified MLB teams over the specified years
        years: list of ints/strings indicating over which years to scrape salary data for the specified MLB teams
        teams: dictionary containing team keys and names in the format of the teams dictionary below
        split: boolean value indicating whether or not the master salary csv file should be split into two csv files of seperate batter and
               pitcher salary information
        batter_salaries_path: string value used as title to create new csv file containing salary data on only batters
        pitcher_salaries_path: string value used as title to create new csv file containing salary data on only pitchers
    """

    '''The names of the columns of the tables extracted from Spotrac. Since the exact headers used in Spotrac vary based on the team/year, 
    these generic headers are used to avoid confusion'''
    spotrac_col_names = ['age','status','base_salary','signing_bonus','incentives','total_salary','adjusted_salary','payroll_perc','active','lux_tax','year','team','key']
    players_col_names = ['key','name','position','spotrac_link']

    #create empty csvs to add player and salary data to
    create_empty_csv(players_csv_path, players_col_names)
    create_empty_csv(salaries_csv_path,spotrac_col_names)
    start_time = time.time()
    for year in years:
        print('Year {year} started at:'.format(year=year))
        print('Time: {}'.format(as_hours(time.time()-start_time)))
        for key , value in teams.items():
            salary_scraper(key,value,year,players_csv_path,salaries_csv_path)
    
    #drop duplicated players from player_csv
    drop_duplicated(players_csv_path)

    if split:
        split_salaries(players_csv_path,salaries_csv_path,batter_salaries_path,pitcher_salaries_path)

if __name__ == "__main__":
    main(players_csv, salaries_csv, years=years, teams=teams, split=True, batter_salaries_path=batter_salaries_csv, pitcher_salaries_path=pitcher_salaries_csv)