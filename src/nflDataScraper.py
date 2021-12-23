# nflWinPrediction/src/nflDataScraper.py

'''
Script for predicting NFL Win totals
Sharp article here: https://www.sharpfootballanalysis.com/betting/numbers-that-matter-for-predicting-nfl-win-totals-part-one/
Scrapes Pro-Football Reference for data
'''

import os
import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr


class winPredictor(object):
    '''
    This class scrapes Pro-Football-Reference.com for the 3 stats most highly correlated with NFL win %:
        - Turnover differential (turnovers created - turnovers committed)
        - Point differential (points for - points against)
        - One-score game win %
        
    class parameters:
        season - (int or str); season desired for statistics pull (should be consistent across method calls)
        team - str; if team != "All", only retrieves desired statistics for one team
    '''

    def __init__(self, season=2020, team='All'):
        self.season = season
        self.team = team

    def get_pt_diff(self, return_teams=True):
        '''
        Scrapes PFR for point differential
        
        parameters:
            return_teams - boolean (default True);
                            if True, the pandas.DataFrame returned will include team names in the index
        '''
        # Scraping season data from PFR
        standings_url = f'https://www.pro-football-reference.com/years/{self.season}/'
        dfs = pd.read_html(standings_url)
        df = pd.concat(dfs)

        # Dropping standings footnotes (*/+) and division labels from the table
        divisions = ['NFC West', 'NFC South',
                     'NFC North', 'NFC East',
                     'AFC West', 'AFC South',
                     'AFC North', 'AFC East']
        df['Tm'] = df['Tm'].str.replace('*','')
        df['Tm'] = df['Tm'].str.replace('+','')
        
        df.index = df['Tm']
        df = df.drop(divisions, axis=0)
        csv_path = os.path.join('..', 'data', 'standings', f'nfl_standings-{self.season}.csv')
        df.to_csv(csv_path)
        
        # Dropping team names as series index labels if desired (default True)
        if not return_teams:
            df.index = np.arange(0,len(df), 1)
            
        # Selecting a single team's Pt Diff if desired by user
        if self.team != "All":
            df = df.loc[df['Tm']==self.team]

        return pd.to_numeric(df['PD'])

    def one_score_record(self, team='All'):
        '''
        Scrapes PRF Results and returns # Wins, # Losses, and Win % for all (or selected) teams in one-score games (8-pt differential or less)
        
        parameters:
            team - str, (default All), searches for all teams if
            
        returns:
                close_wins_by_team - pandas value_counts series of # of wins in one-score games for all teams (or a single team, if team != "All".
                close_loss_by_team - pandas value_counts series of # of losses in one-score games for all teams (or a single team, if team != "All".
                close_game_win_pct - pandas.Series of win % (close wins/close wins + close losses) in one-score games for all teams (or a single team, if team != "All".
        '''
        url = f"https://www.pro-football-reference.com/years/{self.season}/games.htm"
        
        df = pd.read_html(url)[0].drop(['Unnamed: 5'], axis=1)
        df = df.drop_duplicates(keep=False)

        # Adding point diff column and selecting one-score games
        df['PD'] = pd.to_numeric(df['PtsW']) - pd.to_numeric(df['PtsL'])
        close_games = df.loc[df['PD']<=8.0]
        
        # Getting # of close games by team
        close_wins_by_team = close_games['Winner/tie'].value_counts()
        close_loss_by_team = close_games['Loser/tie'].value_counts()

        # If only one or several teams are desired
        if team != 'All':
            close_wins_by_team = close_wins_by_team[team]
            close_loss_by_team = close_loss_by_team[team]
            
        # Win % in one-score games by team - pandas Series with Name
        close_game_win_pct = round(pd.Series((close_wins_by_team / (close_wins_by_team + close_loss_by_team)), name='CGR'), 3)
        
        return close_wins_by_team, close_loss_by_team, close_game_win_pct
            
            
    def turnover_margin(self):
        '''
        Returns Turnover margin for all teams in a given season
            
        returns:
            to_for - pandas.Series object; turnovers created (i.e. defensive turnovers) in a given season for each team
            to_against - pandas.Series object; turnovers committed (i.e. offensive turnovers) in a given season for each team
            to_diff - pandas.Series object; turnovers differential (to_for - to_diff) in a given season for each team
        '''
        # Reading in TOs for each team's defense (turnovers created) and dropping multi-index
        url_def = f"https://www.pro-football-reference.com/years/{self.season}/opp.htm"
        ddf = pd.read_html(url_def)[0]
        ddf.columns = [c[1] for c in ddf.columns]
        
        # Getting Offenseive turnovers committed
        url_off = f"https://widgets.sports-reference.com/wg.fcgi?css=1&site=pfr&url=%2Fyears%2F{self.season}%2F&div=div_team_stats"
        odf = pd.read_html(url_off ,displayed_only=False)[0]
        odf.columns = [c[1] for c in odf.columns] # Getting rid of multi-index for cols
        odf = odf.iloc[0:32:]

        # re-indexing for team labels
        ddf.index, odf.index = ddf['Tm'], odf['Tm']
        ddf = ddf.drop(['Avg Team', "Avg Tm/G", "League Total"], axis=0)

        # Calculating turnover differential for all teams
        to_for = ddf['TO']
        to_against = odf['TO']
        to_diff = to_for - to_against
        
        return to_for, to_against, to_diff
        
    def candlestick_stats(self, save_csv=False):
        '''
        Returns predictive inputs for out model in a pandas dataframe
        
        Needed data:
            - team
            - turnover diff
            - pt diff
            - close game record

        parameters:
            save_csv : boolean, default False; if True, output dataframe saved to a csv file
        '''
        
        to_f, to_a, to_diff = self.turnover_margin()
        c_w, c_l, c_pct = self.one_score_record()
        pt_diff = self.get_pt_diff()
        
#        Combining series into a singular df
        df = pd.concat([to_diff, c_pct, pt_diff], axis=1)
        
        print(f'Candlestick stats by team for {self.season}:')
        print(df.head())
        
        if save_csv:
            csv_path = os.path.join('..', 'data', f'nfl-candlestick-stats-{self.season}.csv')
            df.to_csv(csv_path, index=False)
        return df
    
    def win_loss_pct(self, season=2020):
        '''
        Returns recorded total win/loss % for each team for a given season

        parameters:
            season - int or str (default 2020); season for which turnover stats are deisred
            
        returns:
            pandas.Series object containing total win-loss % for each NFL team
        
        '''
        print('Getting Win-Loss %s')
        standings_url = f'https://www.pro-football-reference.com/years/{self.season}/'
        dfs = pd.read_html(standings_url)

        df = pd.concat(dfs)
        divisions = ['NFC West', 'NFC South', 'NFC North', 'NFC East',
                     'AFC West', 'AFC South', 'AFC North', 'AFC East']

        
        df['Tm'] = df['Tm'].str.replace('*','')
        df['Tm'] = df['Tm'].str.replace('+','')
        df.index = df['Tm']
        df = df.drop(divisions, axis=0)

        return df['W-L%']

    def get_winning_pcts():
        '''
        Returns dict of all possible NFL records (without ties) and winning % with 17-game schedule
        
        returns:
            records - dict {<record>: <Win %>} i.e. {"9-7": .529}
        '''
        w=0
        l = 17
        records = {}
        while w <= 17 and l >= 0:
            win_pct = w/(w + l)
            records[f'{w}-{l}'] = round(win_pct, 3)
            
            w += 1
            l -= 1

        return records


if __name__ == "__main__":    
    w = winPredictor(season=2020)
    w.candlestick_stats()

