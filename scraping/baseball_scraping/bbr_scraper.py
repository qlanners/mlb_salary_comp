'''
file name: bbr_scraper.py
date created: 1/23/19
last edited: 3/15/19
created by: Quinn Lanners
description: this python script takes as input 2 csv files (one a list of players and the other their salary information scraped from www.Spotrac.com
			 using the salary_scraper.py file). It then scrapes salary data for each of the players whose salary was scraped, pulling the
			 statistics from www.baseballreference.com. Along with saving a csv file to the current working directory (with the name passsed
			 as an argument in the function), the script also prints a list of the players for which it failed to retrieve stats.
'''


'''
import all packages. 
	-math used to convert time of seconds into hours and minutes
	-pandas used for dataframe
	-pickle used to save list of unfound players as a variable which can be uploaded into bbr_missing_players_scraper.py to futher attempt to retrieve these players
	-time used to track the duration of the task
	-Selenium used to scrape data from web using an instance of Chrome in the background.
	
'''
import math
import pandas as pd
import pickle
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException


'''
as_hours:
		args:
			s: time in seconds
		returns:
			string of 'hours minutes seconds'
		this function takes as input a time in seconds (determined by the time package) and
		returns of string of hours minutes and seconds for readability purposes
'''
def as_hours(s):
	m = math.floor(s / 60)
	h = math.floor(m / 60)
	s -= m * 60
	m -= h * 60
	return '%dh %dm %ds' % (h, m, s)


'''
look_up_function:
		args:
			name: string value of the name of the player in the format [first 5 letters of last name]+[first two letters of first name]
			year: int or string value of year
			number: string of a number in the format '01','02',... which is appended to name to create bbr ID
			pitcher: boolean value specifying whether player is a pitcher or not
		returns:
			standard: pandas dataframe containing the standard batting table from bbr
			value: pandas dataframe containing the player value--batting table from bbr
				**returns None if these tables are unable to be found for the appropriate year
		this function creates a url given the args with which it attempts to open a headless version of chrome and scrape the
		'Standard Batting' and the 'Player Value--Batting' tables if a positional player and the 
		'Pitching Standard' and 'Pitching Value' tables if a pitcher from the correct baseball reference page.
'''
def look_up_function(name, year, number, pitcher=False):

	option = Options()
	option.add_argument(" - incognito")
	option.add_argument("--no-startup-window")
	option.add_argument("--headless")

	capa = DesiredCapabilities.CHROME
	capa["pageLoadStrategy"] = "none"

	'''ensure that the executable_path points to the directory where your chromedriver is installed (note this code is optimized for 
	google cloud services and thus the path will be different if being run on local computer)'''
	driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', chrome_options = option, desired_capabilities = capa)
	
	#have the chromedriver wait 10 seconds if page isn't instantly located
	wait = WebDriverWait(driver, 10)

	#create url for player from passsed name and number
	url = "https://www.baseball-reference.com/players/"+name[0]+"/"+name+number+".shtml"

	driver.get(url)

	if pitcher:
		wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='pitching_value']")))
	else:
		wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='batting_value']")))


	#pull appropriate tables from website depending on whether the player is a positional player or a pitcher
	if pitcher:
		standard = driver.find_element_by_xpath("//*[@id='pitching_standard']").get_attribute('outerHTML')
		value = driver.find_element_by_xpath("//*[@id='pitching_value']").get_attribute('outerHTML')
	
	else:		
		standard = driver.find_element_by_xpath("//*[@id='batting_standard']").get_attribute('outerHTML')
		value = driver.find_element_by_xpath("//*[@id='batting_value']").get_attribute('outerHTML')

	driver.execute_script("window.stop();")

	driver.stop_client()
	driver.close()


	standard = pd.read_html(standard)
	value = pd.read_html(value)


	standard = standard[0]
	value = value[0]

	'''check to ensure that the player has stats for the year from which the salary was scraped, used as
	one of the checks to ensure it is the correct player'''
	if str(year) not in standard.Year.values:
		return None

	standard_unnamed_cols = [s for s in list(standard) if "Unnamed" in s]
	value_unnamed_cols = [s for s in list(value) if "Unnamed" in s]

	standard.drop(standard_unnamed_cols, axis=1, inplace=True)
	value.drop(value_unnamed_cols, axis=1, inplace=True)

	return standard, value


'''
scrape_data:
		args:
			player_csv_path: string value indicating the location of the csv containing player data
							 scraped using salary_scraper.py
			salary_csv_path: string value indicating the location of the csv containing salary data
							 scraped using salary_scraper.py
			bbr_data_csv_path: string value indicating the name of the new csv file to be created containing
							   the bbr_data salary and batting/pitching statistics data
			pitchers: indicates whether the player_csv_path contains positional players or pitchers
							 (stats for positional players and pitchers must be scraped seperately, 
							 hence the split_salaries function from the salary_scraper file)
			first_last: depending on your operating system, the split salaries may have names in the format 
							 "Last Name First Name" or "First Name Last Name". Check the format of the outputted 
							 players_csv_path from split_salaries.py. If the player names are in the format 
							 "First Last" then keep as True. Else if the player names are in the format
							 "Last First" then False.
		returns:
			None
		This function iterates through each player for which salary information was scraped, and scrapes their
		full career statistics from baseballreference. While doing so, it keeps track of the players whose stats
		where unable to be retrieved. In the end, this function saves a csv to the current working directory 
		which contains statistics scraped from basbeballreference for each player, along with prints and saves lists
		which are a summary of the players whose statistics were unable to be scraped using the rather hack way that
		URLs where created with which to load their stats page in bbr.
'''
def scrape_data(players_csv_path, salary_csv_path, bbr_data_csv_path, pitchers=False, first_last=True):
	
	#creates datafames for player and salary data
	players = pd.read_csv(players_csv_path)
	salaries = pd.read_csv(salary_csv_path)
	
	#left join the tables with salares on left
	joined = salaries.merge(players, on='key', how='left')
	if pitchers:
		print('Number of player salaries to match to pitching statistics: {}'.format(len(joined['key'].values)))
	else:	
		print('Number of player salaries to match to batting statistics: {}'.format(len(joined['key'].values)))

	#list of the leagues from which we desire to scrape information. Used to avoid scrapping stats from A,AA,AAA ball
	leagues = ['AL','NL','MLB']

	#empty datafame which will we add bbr_data salary and stat data from bbr
	bbr_data = pd.DataFrame()

	start_time = time.time()

	#used to track the players which the script fails to join data on
	missed_players = list()
	missed_players_keys = list()
	misses = 0
	players_done = []



	#iterates through each row in the joined dataframe, taking the year, age, and name value out of each row to input into the look_up_function
	for salary_index, salary_row in joined.iterrows():
		
		#checks to see if this player has already hade his stats scraped, if so, skip player
		if salary_row['key'] not in players_done:
			year = str(salary_row['year']).split('.')[0]
			age = int(salary_row['age'])
			name_parts = str(salary_row['name']).replace('.','').replace("'","").lower().split()
			name_parts_check = str(salary_row['name']).replace("'","").lower().split()
			
			#used to deal with players that may have multiple last names/two parts to last name (ex. 'Abel De Los Santos')
			if first_last:
				if len(name_parts) == 2:
					name = name_parts[1][:5]+name_parts[0][:2]
					name_check = name_parts_check[1][:5]+name_parts_check[0][:2]
				if len(name_parts) == 3:
					name = name_parts[1][:5] + name_parts[2][:(5-len(name_parts[1][:5]))] + name_parts[0][:2]
					name_check = name_parts_check[1][:5] + name_parts_check[2][:(5-len(name_parts_check[1][:5]))] + name_parts_check[0][:2]
				
			else:
				if len(name_parts) == 2:
					name = name_parts[0][:5]+name_parts[1][:2]
					name_check = name_parts_check[0][:5]+name_parts_check[1][:2]
				if len(name_parts) == 3:
					name = name_parts[0][:5] + name_parts[1][:(5-len(name_parts[0][:5]))] + name_parts[2][:2]
					name_check = name_parts_check[0][:5] + name_parts_check[1][:(5-len(name_parts_check[0][:5]))] + name_parts_check[2][:2]
			
			

			'''
			these numbers are inputted to the look_up_function. The first time through, 01 is inputted to create an id with [name]01. If
			this combination doesnt work, then the second time through 02 is inputted into the look_up_function, creating an id with [name]02
			and the loop continues like this, trying up to the id [name]11. This is used to deal with the fact that bbr makes player ids based
			off of a name/number combo, where they simply count up starting at 01 as player names are duplicated. 11 was chosen, as that was the
			highest number that was encountered. 

			***To shorten the duration of the code, feel free to shorten this list. However, be aware you may miss a 
			few more players that otherwise would have been scraped.***
			'''
			numbers = ['01','02','03','04','05','06','07','08','09','10','11']
			
			count = 0
			while count <= 10:
				try:
					standard, value = look_up_function(name,year,numbers[count],pitcher=pitchers)
					
					#variables created as checks to ensure this is the appropriate player (to handle players with duplicate names)
					verify_player_row = standard.loc[standard['Year'] == str(year)]
					possible_ages = [str(age-1),str(age),str(age+1)]
					if str(int(verify_player_row['Age'].values[0])) in possible_ages:
						standard.loc[standard['Lg'].isin(leagues)]
						standard = standard.loc[standard['Lg'].isin(leagues)]
						value = value.loc[value['Lg'].isin(leagues)]
						standard['join_key_y'] = standard['Year'] + standard['Tm']
						value['join_key_y'] = value['Year'] + value['Tm']
						total_stats = standard.merge(value, on='join_key_y', how='left', suffixes=('', '_y'))
						total_stats['key'] = salary_row['key']
						total_stats.drop(list(total_stats.filter(regex = '_y')), axis = 1, inplace = True)

						#for first player scraped, label the columns of the database
						if bbr_data.shape[1] < 20:
							all_headers = list(total_stats)
							bbr_data = bbr_data.reindex(columns=all_headers)
							bbr_data = bbr_data.astype('object')
						
						bbr_data = bbr_data.append(total_stats, ignore_index=True)

						players_done.append(salary_row['key'])
						if salary_row['name']+' '+name in missed_players:
							misses_fixed = missed_players.count(salary_row['name']+' '+name)
							missed_players = [player for player in missed_players if player != salary_row['name']+' '+name]
							missed_players_keys.remove(salary_row['key'])
							misses -= misses_fixed

						#if all of the above code executed, count is set to a number greater than 10 to exit the loop for this player
						count = 21

					#if url lookup worked for this player ID, but the page didn't match the current player, try again using next number
					else:
						count += 1
				
				# if the url lookup didn't work for this player ID, try again using next number
				except:
					if count == 10 and name != name_check:
						name = name_check
						count =0
					else:
						count += 1

			#if the player information could not be scraped for ID number 01-11, then print name and add to missed players list
			if count > 10 and count != 21:
				print('{full_name} {id} {year}'.format(full_name=salary_row['name'], id=name, year=year))
				missed_players.append(salary_row['name']+' '+name)
				if salary_row['key'] not in missed_players_keys:
					missed_players_keys.append(salary_row['key'])
				misses += 1

			#print the elapsed time after every 100 analyzed players
			else:
				if (salary_index % 100) == 0:
					print('...'+str(salary_index)+'...')
					print('Time: {}'.format(as_hours(time.time()-start_time)))
					print('')


	#save the bbr_data table to a csv in the current directory
	bbr_data.to_csv(bbr_data_csv_path, index=False)

	#print a list of all of the missed players and their keys, along with the number of missed players
	unique_missed_players = list(dict.fromkeys(missed_players))
	print('')

	#Dump missing players list to pickle variable to load later in the bbr_missing_players_scraper.py script
	if pitchers:
		pickle_file_prefix = 'pitchers'
	else:
		pickle_file_prefix = 'batters'
	with open(pickle_file_prefix+'_players.pickle', 'wb') as file:
		pickle.dump(unique_missed_players, file)
	with open(pickle_file_prefix+'_keys.pickle', 'wb') as file:
		pickle.dump(missed_players_keys, file)	

	print(unique_missed_players)
	print(missed_players_keys)
	print('{} unique players missed'.format(len(unique_missed_players)))
	print('')
	print('Salary years without stats: {misses} of {total}'.format(misses=misses, total=salaries.shape[0]))
	print('Time: {}'.format(as_hours(time.time()-start_time)))
	print('')
	print('')



scrape_data('players.csv','batters.csv','batters_bbr.csv',pitchers=False,first_last=True)
scrape_data('players.csv','pitchers.csv','pitchers_bbr.csv',pitchers=True,first_last=True)