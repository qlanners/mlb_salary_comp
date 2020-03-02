#create a database file (sqllite) from all the data scraped
import pandas as pd
import sqlite3

meta = pd.read_csv('meta.csv')
meta = meta[['NAME_KEY','NAME', 'BATS', 'THROWS', 'HEIGHT','HEIGHT_CM', 'WEIGHT_LB', 'WEIGHT_KG', 'BIRTHDATE', 'BIRTHPLACE']]
meta = meta.drop_duplicates('NAME_KEY')

fa = pd.read_csv('free_agents.csv')
fa = fa[['NAME_KEY', 'NAME', 'YEAR', 'ARRIVAL_DT', 'ARRIVAL_METHOD', 'WAS_DRAFTED', 'DRAFT_ROUND', 'SIGNED_DT',
       'AGE_WHEN_SIGNED', 'FREE_AGENT_DT', 'IS_FREE_AGENT_NOW', 'SEASON_START_DT', 'PLAYER_URL']]

pvb =  pd.read_csv('player_value_batting.csv')
pvb = pvb[['NAME_KEY', 'NAME', 'TM', 'LEAGUE', 'YEAR', 'G', 'PA', 'RBAT', 'RBASER',
       'RDP', 'RFIELD', 'RPOS', 'RAA', 'WAA', 'RREP', 'RAR', 'WAR', 'WAAWL%',
       '162WL%', 'OWAR', 'DWAR', 'ORAR', 'SALARY', 'ACQUIRED']]
pvb = pvb.rename(columns={"WAAWL%": "pct_WAAWL", "162WL%": "pct_162WL"})

df_list = [meta, fa, pvb]
table_list = ['Meta', 'Free_agents', 'player_value_batting']

conn = sqlite3.connect('baseball_reference.sqlite')
cur = conn.cursor()



cur.executescript(
"""
DROP TABLE IF EXISTS Meta;
CREATE TABLE Meta ( NAME TEXT,NAME_KEY TEXT, BATS TEXT, THROWS TEXT,
                    HEIGHT TEXT, HEIGHT_CM DECIMAL(15,3),
                    WEIGHT_LB INTEGER, WEIGHT_KG DECIMAL(15,3),
                    BIRTHDATE DATE, BIRTHPLACE TEXT);

DROP TABLE IF EXISTS Free_agents;
CREATE TABLE Free_agents ( NAME_KEY TEXT, NAME TEXT, YEAR INTEGER, ARRIVAL_DT DATE,
                            ARRIVAL_METHOD TEXT, WAS_DRAFTED TEXT, DRAFT_ROUND TEXT,
                            SIGNED_DT DATE, AGE_WHEN_SIGNED INTEGER, FREE_AGENT_DT DATE,
                            IS_FREE_AGENT_NOW TEXT, SEASON_START_DT DATE, PLAYER_URL TEXT );

DROP TABLE IF EXISTS player_value_batting;
CREATE TABLE player_value_batting ( NAME TEXT, NAME_KEY TEXT, TM TEXT, LEAGUE TEXT, YEAR INTEGER,
                                    G INTEGER, PA DECIMAL(15,3), RBAT INTEGER,
                                    RBASER INTEGER, RDP INTEGER, RFIELD INTEGER,
                                    RPOS DECIMAL(15,3), RAA DECIMAL(15,3), WAA DECIMAL(15,3),
                                    RREP DECIMAL(15,3), RAR DECIMAL(15,3), WAR DECIMAL(15,3),
                                    pct_WAAWL DECIMAL(15,3), pct_162WL DECIMAL(15,3), OWAR DECIMAL(15,3),
                                    DWAR DECIMAL(15,3), ORAR DECIMAL(15,3), SALARY DECIMAL(15,3) , ACQUIRED TEXT)
""")

for df,table in zip(df_list, table_list):
    df.to_sql(table, con=conn, if_exists='append', index=False)
