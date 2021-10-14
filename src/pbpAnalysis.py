# Script to format data for Play-by-play (pbp) analysis of NFL Games
# Scrapes pbp data from pro-football ref

import pandas as pd
import numpy as np
#from sqlalchemy import create_engine
import sqlalchemy as db
import time


#sample_url = "https://widgets.sports-reference.com/wg.fcgi?css=1&site=pfr&url=%2Fboxscores%2F202109090tam.htm&div=div_pbp"
sample_url = "https://widgets.sports-reference.com/wg.fcgi?css=1&site=pfr&url=%2Fboxscores%2F202109120atl.htm&div=div_pbp"

team_codes = {'Dallas Cowboys':'dal', 'Atlanta Falcons':'atl',
              'New York Jets':'nyj', 'Minnesota Vikings':'min',
              'Indianapolis Colts': 'clt', 'Detroit Lions': 'det',
              'Buffalo Bills': 'buf', 'Tennessee Titans': 'oti',
              'Jacksonville Jaguars': 'jax', 'Washington Football Team': 'was',
              'Cleveland Browns': 'cle', 'New England Patriots':'nwe',
              'New York Giants': 'nyg', 'Green Bay Packers': 'gnb',
              'Chicago Bears': 'chi', 'Baltimore Ravens': 'rav',
              'Miami Dolphins': 'mia', 'Cincinnati Bengals': 'cin',
              'Pittsburgh Steelers': 'pit','New Orleans Saints': 'nor',
              'Houston Texans':'htx', 'Philadelphia Eagles':'phi',
              'Seattle Seahawks': 'sea', 'Los Angeles Chargers': 'lac',
              'Kansas City Chiefs': 'kan', 'Tampa Bay Buccaneers': 'tam',
              'San Francisco 49ers': 'sfo', 'Los Angeles Rams': 'lar',
              'Denver Broncos': 'den', 'Carolina Panthers': 'car',
              'Las Vegas Raiders':'rai', 'Arizona Cardinals': 'crd',
#              Relocated teams
              'Oakland Raiders': 'rai', 'St. Louis Rams':'ram',
              'San Diego Chargers': 'sdg', 'Washington Redskins': 'was',
              'Tennessee Oilers': 'oti'
              
}
            #KC-Browns embed link:
#script src="https://widgets.sports-reference.com/wg.fcgi?css=1&site=pfr&url=%2Fboxscores%2F202109120kan.htm&div=div_pbp

# Need to find a way to source game dates and re-format them (as well as home team
sched_url = "https://www.pro-football-reference.com/years/2021/games.htm#games"


def get_nfl_schedule(season):
    '''
    Pulls NFL Schedule from pro-football-reference.com
    
    parameters:
        season - int or str; season desired
    '''
#    Reading in and re-formatting NFL season sched
    url = f"https://www.pro-football-reference.com/years/{season}/games.htm#games"
    df = pd.read_html(url, header=0, displayed_only=True)[0]
    df = df[(df['Week']!='Week') & (df['Date']!='Playoffs')]
    df.columns = ['Week', 'Day', 'Date', 'Time', 'Winner/tie', 'location',                  'Loser/tie', 'Unnamed: 7', 'PtsW', 'PtsL', 'YdsW',  'TOW',              'YdsL', 'TOL']
#    Setting home & away teams based on location column
#    If there's an @ symbol, the loser/tie column is the home team
    df['Home Team'] = np.where(df['location']=='@', df['Loser/tie'], df['Winner/tie'])
    df['Away Team'] = np.where(df['location']=='@', df['Winner/tie'], df['Loser/tie'])
    
    df['Date Formatted'] = [d.replace("-", "") for d in df['Date']]
    print(df.head())

    return df

def get_pbp(url):
    '''
    Gets play-by-play data for a given NFL game.
    Scrapes data from pro-football-reference.com
    
    parameters:
        url - str; url to table included in
    '''
    return pd.read_html(url, displayed_only=True)[0].drop(0, axis=0)

def construct_pbp_db(start=1997, end=2020):
    '''
    Constructs database of every NFL play
    
    Loops through each NFL season (default 2020 - 1997).
    Scrapes pro-football reference for the NFL Schedule that year
    Then scrapes each individual game in that season
    Dumps results to our local db file (could host this on a MySQL server)
    
    parameters:
        start : str or int; beginning year (default 1997)
        end : str or int; ending year for search (default 2020)
        
    '''
#   Loops through each game in a season (can be changed) and produces play-by-play log for each game in that season
    engine = db.create_engine('sqlite:///../db/nfl.db', echo=False)

    for year in range(start, end):
        print(year)
        sched = get_nfl_schedule(year)
        
        #    Writing schedule df to a db to test out sqlalchemy
        print('#######################################')
        
        with engine.begin() as connection:
            sched.to_sql(f'schedule{year}', con=connection, if_exists='replace')

            print('db queried!')
        print('#######################################')

        for index, row in sched.iterrows():
            print(f"{row['Home Team']} vs. {row['Away Team']} {row['Date']}")
            game_date = row['Date Formatted']
            home_team = team_codes[row['Home Team']]
            url = f"https://widgets.sports-reference.com/wg.fcgi?css=1&site=pfr&url=%2Fboxscores%2F{game_date}0{home_team}.htm&div=div_pbp"
            print(f'Scrape URL: {url}')
            
            try:
#                Grabbing play-by-play
                df = get_pbp(url)
                
                print(df.head())
                with engine.begin() as connection:
                    df.to_sql(f'{home_team}{game_date}', con=connection, if_exists='replace')

                    print('Play-by-Play inserted into db!')
            except:
                pass
            
            print('--------------------------------------------------------------')
        
#        Don't want PFR to mark our IP address, now would we?
        time.sleep(10)
    print('SQLite DB created: ../db/nfl.db')

def query_pbp_db(query="SELECT * FROM "):
    '''
    Queries our local nfl.db file (or the one created by construct_pbp_db)
    
    Utilizes pandas.read_sql functionality to enact the query
    '''
    engine = db.create_engine('sqlite:///../db/nfl.db', echo=False)
    tables = engine.table_names()

    df = pd.read_sql(query, con=engine)
#    db.clear_compiled_cache()
    
    return df

if __name__=="__main__":
#    Only need to call this to append to for 2021 (maybe 2020 season)
    construct_pbp_db(1999,2020)
#    eng = db.create_engine('sqlite:///../db/nfl.db', echo=False)
#    tables = eng.get_table_names()
#
#    for t in tables[0:10]:
#        print(f'Table: {t}')
#        q = f"SELECT * FROM {t};"
#        print(q)
#        pbp = query_pbp_db(q)
#        print(pbp.head())
#        print(pbp['Detail'])
#        print('==============================================================')
