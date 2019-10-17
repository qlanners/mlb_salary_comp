import requests
import bs4
import pandas as pd
from time import perf_counter
from math import floor

'''
The objective of this scraper is
to grab, for each player, for each year,
grab meta data
'''
start = perf_counter()




#lists for personal attributes

NAME = []
NAME_KEY = []
YEAR = []
TEAM = []

#lists for meta data
BATS = []
THROWS = []
HEIGHT = []
HEIGHT_CM = []
WEIGHT_LB = []
WEIGHT_KG = []
BIRTHDATE = []
BIRTHPLACE = []

miss_counter = 0
try_counter = 0

misses = open('meta_misses.txt', 'w')

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


                url_PG = "https://www.baseball-reference.com/players/gl.fcgi?id=" + namekey + "&t=b&year=" + year
                res_PG = requests.get(url_PG)
                soup_PG=bs4.BeautifulSoup(res_PG.text, 'html.parser')

                meta = soup_PG.find('div', {'id':'meta'})

                for p in meta.find_all('strong'):

                    if p.text == "Bats: ":
                        bats = p.next_sibling.replace('\n','').replace(' ','').replace('\xa0','').replace('•','').replace('\t','')

                    if p.text == "Throws: ":
                        throws = p.next_sibling.replace('\n','').replace(' ','').replace('\xa0','').replace('•','').replace('\t','')

                height = meta.find('span', {'itemprop':'height'}).text
                weight_lb = int(meta.find('span', {'itemprop':'weight'}).text[:-2])
                birthdate = meta.find('span',{'id':'necro-birth'}).get("data-birth")
                birthplace = meta.find('span',{'itemprop':'birthPlace'}).find_next('span').text
                h_ft = int(height.split('-')[0])
                h_in = int(height.split('-')[1])
                h_inch = h_in + h_ft * 12
                h_cm = h_inch * 2.54
                weight_kg = weight_lb*0.453592


                NAME.append(name)
                NAME_KEY.append(namekey)
                YEAR.append(year)
                TEAM.append(team)
                BATS.append(bats)
                THROWS.append(throws)
                HEIGHT.append(height)
                HEIGHT_CM.append(h_cm)
                WEIGHT_LB.append(weight_lb)
                WEIGHT_KG.append(weight_kg)
                BIRTHDATE.append(birthdate)
                BIRTHPLACE.append(birthplace)

                print(try_counter, '- success', '- ',year, ' ', perf_counter() - start)
            except:

                miss_counter += 1
                misses.write(str(miss_counter) + ' - ' + url_PG + '\n')
                print(try_counter, '- miss', '- ', name)
misses.close()




data_dict = {
"NAME": NAME,
"NAME_KEY": NAME_KEY,
"YEAR": YEAR,
"TEAM":TEAM,
"BATS": BATS,
"THROWS": THROWS,
"HEIGHT": HEIGHT,
"HEIGHT_CM": HEIGHT_CM,
"WEIGHT_LB": WEIGHT_LB,
"WEIGHT_KG": WEIGHT_KG,
"BIRTHDATE": BIRTHDATE,
"BIRTHPLACE": BIRTHPLACE
}

df = pd.DataFrame(data_dict)
df.to_csv('meta.csv', mode='w', header = True, index = False)


end = perf_counter()
elapsed = end - start

hours   = floor(elapsed / 60**2)
minutes = floor((elapsed - hours*60**2) / 60)
seconds = floor(elapsed - hours*60**2 -minutes*60)

meta_runtime = open('meta_runtime.txt', mode = 'w')
meta_runtime.write('\n ++++++++++++++++++++++++++++++++++++++++ END ++++++++++++++++++++++++++++++++++++++++ \n')
meta_runtime.write(f'\n Elapsed Time:  {hours} hours, {minutes} minutes, {seconds} seconds \n Number of players tried: {try_counter}\n Number of misses: {miss_counter}')
meta_runtime.close()
