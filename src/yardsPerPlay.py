# Script to determine yards-per play and NFL rank for each superbowl winner

import pandas as pd
import numpy as np



#https://www.pro-football-reference.com/years/2021/#team_stats

def yardsPerPlay(season):
    '''
    Scrapes pro-football reference for yards/play stats for each NFL team in a season
    
    parameters:
        season - int or str; season for which stats are desired
    
    returns:
        df - pandas.DataFrame object; contains candlestick offensive stats for each NFL team in a season
    '''
    url = f"https://widgets.sports-reference.com/wg.fcgi?css=1&site=pfr&url=%2Fyears%2F{season}%2Findex.htm&div=div_team_stats"
    df = pd.read_html(url, displayed_only=False)[0]
    df.columns = [c[1] for c in df.columns]

    df = df.iloc[0:32]
    df = df.sort_values(by=['Y/P'], ascending=False)
    df.reset_index(inplace=True)
    df = df.drop(['index', 'Rk'], axis=1)
    
    print(df)
    
    return df

def superBowlWinners():
    '''
    Gets list of superbowl matchups and winners
    Scrapes Pro-football reference
    https://www.pro-football-reference.com/super-bowl/
    
    returns:
        df - pandas.DataFrame object containing historical Super Bowl matchups
    '''
    url = "https://www.pro-football-reference.com/super-bowl/"
    df = pd.read_html(url)[0]
    
#    Adding Season col to make lookup easier
    df['Season'] = [(int(d.split(" ")[2])-1) for d in df['Date']]
    df['Season'] = df['Season'].astype(int)
    print(df.head())
    
    return df

if __name__ == "__main__":
    sb = superBowlWinners()
#    yardsPerPlay(2020)
    print(sb['Winner'])
    yardage = []
    ranks = []
    for s in range(2020, 2002,-1):
        print(s)
        sb_winner = sb['Winner'].loc[sb['Season']==s].values[0]
#        sb_winner = sb_winner['Winner']
        print(f'Super Bowl Winner in {s}: {sb_winner}')
        df = yardsPerPlay(s)
        
        avg_yds_rank = df.index[df['Tm']==sb_winner].values[0] + 1
        avg_yds = df['Y/P'].loc[df['Tm']==sb_winner].values[0]
        
        yardage.append(avg_yds)
        ranks.append(avg_yds_rank)
        
        print(f'{sb_winner} yards-per-play: {avg_yds}')
        print(f'{s} NFL Rank: {avg_yds_rank}')
        print('--------------------------------------')


    print(yardage)
    print(ranks)
