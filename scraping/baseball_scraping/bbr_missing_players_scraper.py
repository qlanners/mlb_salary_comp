'''
file name: bbr_missing_players_scraper.py
date created: 3/14/19
last edited: 3/15/19
created by: Quinn Lanners
description: this python script takes the links and keys of the players missed from the original bbr_scraper.py script and scrapes their data
			 from baseballreference.
'''


'''
import all packages. 
	-Selenium used to scrape data from web using an instance of Chrome in the background.
	-pandas used for dataframe
'''
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
import math
import pickle

'''
look_up_function:
		args:
			link: string value of the URL link to the baseballreference page for that player
			pitcher: boolean value indicating whether the player is a pitcher
		returns:
			standard: pandas dataframe containing the standard batting table from bbr
			value: pandas dataframe containing the player value--batting table from bbr
				**returns None if these tables are unable to be found for the appropriate year
		this function scrapes statistics for a player with their baseballreference link given as an arg
'''
def search_player(player_name, pitcher=False):
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
	wait = WebDriverWait(driver, 30)

	driver.get('https://www.baseball-reference.com/')

	wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='header']/div[3]/form/div/div")))

	stuff = driver.find_element_by_xpath("//*[@id='header']/div[3]/form/div/div/input[2]")

	stuff.send_keys(player_name)

	stuff.send_keys(Keys.RETURN)

	if '/search/' in driver.current_url:
		wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='players']/div[1]/div[1]/a")))
		button = driver.find_element_by_xpath("//*[@id='players']/div[1]/div[1]/a")
		button.click()
	
	if pitcher:
		wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='pitching_value']")))
	else:
		wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='batting_value']")))


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

	standard_unnamed_cols = [s for s in list(standard) if "Unnamed" in s]
	value_unnamed_cols = [s for s in list(value) if "Unnamed" in s]

	standard.drop(standard_unnamed_cols, axis=1, inplace=True)
	value.drop(value_unnamed_cols, axis=1, inplace=True)

	return standard, value