# Script to format data for Play-by-play (pbp) analysis of NFL Games
# Scrapes pbp data from pro-football ref

import pandas as pd
import numpy as np

#sample_url = "https://widgets.sports-reference.com/wg.fcgi?css=1&site=pfr&url=%2Fboxscores%2F202109090tam.htm&div=div_pbp"
sample_url = "https://widgets.sports-reference.com/wg.fcgi?css=1&site=pfr&url=%2Fboxscores%2F202109120atl.htm&div=div_pbp"

team_codes = {'Dallas Cowboys':'dal', 'Atlanta Falcons':'atl',
              'New York Jets':'nyj', 'Minnesota Vikings':'min',
              'Indianapolis Colts': 'ind', 'Detroit Lions': 'det',
              'Buffalo Bills': 'buf', 'Tennessee Titans': 'ten',
              'Jacksonville Jaguars': 'jax', 'Washington Football Team': 'was',
              'Cleveland Browns': 'cle', 'New England Patriots':'nwe',
              'New York Giants': 'nyg', 'Green Bay Packers': 'gnb',
              'Chicago Bears': 'chi', 'Baltimore Ravens': 'bal',
              'Miami Dolphins': 'mia', 'Cincinnati Bengals': 'cin',
              'Pittsburgh Steelers': 'pit','New Orleans Saints': 'nor',
              'Houston Texans':'hou', 'Philadelphia Eagles':'phl',
              'Seattle Seahawks': 'sea', 'Los Angeles Chargers': 'lac',
              'Kansas City Chiefs': 'kan', 'Tampa Bay Buccaneers': 'tam',
              'San Francisco 49ers': 'sfo', 'Los Angeles Rams': 'lar',
              'Denver Broncos': 'den', 'Carolina Panthers': 'car',
              'Las Vegas Raiders':'rai', 'Arizona Cardinals': 'ari'}
            #KC-Browns embed link:
#script src="https://widgets.sports-reference.com/wg.fcgi?css=1&site=pfr&url=%2Fboxscores%2F202109120kan.htm&div=div_pbp

# Need to find a way to source game dates and re-format them (as well as home team
sched_url = "https://www.pro-football-reference.com/years/2021/games.htm#games"
def getNFLSchedule(season):
    '''
    Pulls NFL Schedule from pro-football-reference.com
    
    parameters:
        season - int or str; season desired
    '''
    url = f"https://www.pro-football-reference.com/years/{season}/games.htm#games"
    df = pd.read_html(url, header=0, displayed_only=True)[0]
    df = df[df['Week']!='Week']
    df.columns = ['Week', 'Day', 'Date', 'Time', 'Winner/tie', 'location',                  'Loser/tie', 'Unnamed: 7', 'PtsW', 'PtsL', 'YdsW',  'TOW',              'YdsL', 'TOL']
#    Setting home & away teams based on location column
#    If there's an @ symbol, the loser/tie column is the home team
    df['Home Team'] = np.where(df['location']=='@', df['Loser/tie'], df['Winner/tie'])
    df['Away Team'] = np.where(df['location']=='@', df['Winner/tie'], df['Loser/tie'])
    
    df['Date Formatted'] = [d.replace("-", "") for d in df['Date']]
    print(df.head())

    return df

def getPlayByPlay(url):
    '''
    Gets play-by-play data for a given NFL game.
    Scrapes data from pro-football-reference.com
    
    parameters:
        url - str; url to table included in
    '''
        
    df = pd.read_html(sample_url, header=0, displayed_only=True)[0]

    print(df.head())
    return df

#sample_url = "https://widgets.sports-reference.com/wg.fcgi?css=1&site=pfr&url=%2Fboxscores%2F202109120atl.htm&div=div_pbp"

if __name__=="__main__":
#   Loops through each game in 2020 season (can be changed) and produces play-by-play log for that game
    sched = getNFLSchedule(2020)
    for index, row in sched.head(n=16).iterrows():
        print(f"{row['Home Team']} vs. {row['Away Team']} {row['Date']}")
        game_date = row['Date Formatted']
        home_team = team_codes[row['Home Team']]
        url = f"https://widgets.sports-reference.com/wg.fcgi?css=1&site=pfr&url=%2Fboxscores%2F{game_date}0{home_team}.htm&div=div_pbp"
        df = getPlayByPlay(url)
        print('--------------------------------------------------------------')
