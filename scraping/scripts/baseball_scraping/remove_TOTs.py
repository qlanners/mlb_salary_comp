'''
file name: remove_TOTs.py
date created: 3/14/19
last edited: 3/15/19
created by: Quinn Lanners
description: when player data is scraped from baseball reference for players who played
             for multiple teams in a single year, a row of data is created for each team
             along with a row labeled TOT. Since this TOT row does not include advanced
             statistics, this script worked to reseolve this issue by create a single row
             for a player who played for multiple teams which also includes advanced stats
             (which are calculated using a weighted average)
'''


'''
import all packages. 
    -pandas used for dataframe
'''
import pandas as pd
import os
import glob
import sys


'''
remove_multiple_teams:
        args:
            bbr_data_csv: string of the csv which you wish to remove TOTs from
            pitchers: boolean value indicating if the players are pitchers or not
        returns:
            None
        this function iterates through the specified csv and combines the stats for
        players who played for multiple teams in a year to create a single row of
        player stats for each year
'''
def remove_multiple_teams(bbr_datatype, pitchers=False):
    if bbr_datatype == 'batters':
        csvs = glob.glob('batters_bbr*.csv')
    if bbr_datatype == 'pitchers':
        csvs = glob.glob('pitchers_bbr*.csv')
    print(csvs)
        

    bbr_data = pd.concat([pd.read_csv(i) for i in csvs if os.stat(i).st_size > 2])

    bbr_data=bbr_data.reset_index(drop=True)

    bbr_data[["Year", "key"]].apply(pd.to_numeric)

    
    #create columns to hold second and third team names (if necessary)
    bbr_data['Tm2'] = ""
    bbr_data['Tm3'] = ""
    rows_to_drop = []
    
    '''specifies the columns over which stats should be added and over which a weighted
    average should be taken'''
    if pitchers:
        added_cols = ['W','L','G','GS','GF','CG','SHO','SV','IP','H','R','ER','HR','BB','IBB','SO','HBP','BK','WP','BF']
        weighted_cols = ['W-L%','ERA','ERA+','FIP','WHIP','H9','HR9','BB9','SO9','SO/W','RA9','RA9opp','RA9def','RA9role','PPFp','RA9avg','RAA','WAA','gmLI','WAAadj','WAR','RAR','waaWL%','162WL%']
    else:
        added_cols = ['G','PA','AB','R','H','2B','3B','HR','RBI','SB','CS','BB','SO','TB','GDP','HBP','SH','SF','IBB']
        weighted_cols = ['BA','OBP','SLG','OPS','OPS+','Rbat','Rbaser','Rdp','Rfield','Rpos','RAA','WAA','Rrep','RAR','WAR','waaWL%','162WL%','oWAR','dWAR','oRAR']
    
    print('Rows to check: '+str(bbr_data.shape[0]))
    
    for index, row in bbr_data.iterrows():

        if row["Tm"] == 'TOT':
            player_key = row['key']
            year = row['Year']
            total_teams = bbr_data.loc[bbr_data['key'] == player_key]
            total_teams = total_teams.loc[total_teams['Year'] == year]
            awards = total_teams.iloc[0]['Awards']
            total_games = total_teams.iloc[0]['G']
            if pitchers:
                total_innings = total_teams.iloc[0]['IP']
            total_teams = total_teams[total_teams.Tm != 'TOT']
            no_o_teams = total_teams.shape[0]
            if no_o_teams > 1:
                new_row = total_teams.iloc[0]
                new_row.at['Tm2'] = total_teams.iloc[1]['Tm']
                new_row.at['Awards'] = awards
                if no_o_teams > 2:
                    new_row.at['Tm3'] = total_teams.iloc[2]['Tm']

                
                for col in added_cols:
                    new_row.at[col] = total_teams[col].sum()            

                for col in weighted_cols:
                    weighted_stat = 0
                    for i in range(no_o_teams):
                        if pitchers:
                            weighted_stat += total_teams.iloc[i][col] * (total_teams.iloc[i]['IP'] / total_innings )
                        else:
                            weighted_stat += total_teams.iloc[i][col] * (total_teams.iloc[i]['G'] / total_games )
                    
                    new_row.at[col] = round(weighted_stat,3)
                bbr_data.iloc[index] = new_row

                for i in range(index+1,index+1+no_o_teams):
                    rows_to_drop.append(i)
            else:
                rows_to_drop.append(index)
        if index % 1000 == 0:
            print('.')


    bbr_data.drop(rows_to_drop, inplace=True)

    
    '''creates a new csv file and saved to working directory. Used as a way to not
    overwrite the inputted file in case you wish to reference it later'''
    bbr_data.to_csv(bbr_datatype+'_TOTs_removed.csv', index=False)

player_type = sys.argv[1]

if player_type == 'batters':
    remove_multiple_teams('batters')
    print('Batters Done')
if player_type == 'pitchers':
    remove_multiple_teams('pitchers',pitchers=True)
    print('Pitchers Done')

