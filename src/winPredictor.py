# Script for predicting NFL Win totals
# Sharp article here: https://www.sharpfootballanalysis.com/betting/numbers-that-matter-for-predicting-nfl-win-totals-part-one/
#Scrapes Pro-Football Reference for data

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

    def getPtDiff(self, season, return_teams=True):
        '''
        Scrapes PFR for point differential
        
        parameters:
            season - str or int, year to search for
            return_teams - boolean (default True);
                            if True, the pandas.DataFrame returned will include team names in the index
        '''
        standings_url = f'https://www.pro-football-reference.com/years/{season}/'
        dfs = pd.read_html(standings_url)

        df = pd.concat(dfs)

    #    Dropping standings footnotes (*/+) and division labels from the table
        divisions = ['NFC West', 'NFC South',
                     'NFC North', 'NFC East',
                     'AFC West', 'AFC South',
                     'AFC North', 'AFC East']

        df['Tm'] = df['Tm'].str.replace('*','')
        df['Tm'] = df['Tm'].str.replace('+','')
        
        df.index = df['Tm']
        df = df.drop(divisions, axis=0)
        df.to_csv(f'./standings/nfl_standings-{season}.csv')
        
    #    Dropping team names as series index labels if desired (default True)
        if not return_teams:
            df.index = np.arange(0,len(df), 1)
        
        return pd.to_numeric(df['PD'])

    def oneScoreRecord(self, season, team='All'):
        '''
        Scrapes PRF Results and returns # Wins, # Losses, and Win % for all (or selected) teams in one-score games (8-pt differential or less)
        
        parameters:
            season - str or int, NFL season search is desired for
            team - str, (default All), searches for all teams if
            
        returns:
                close_wins_by_team - pandas value_counts series of # of wins in one-score games for all teams (or a single team, if team != "All".
                close_loss_by_team - pandas value_counts series of # of losses in one-score games for all teams (or a single team, if team != "All".
                close_game_win_pct - pandas.Series of win % (close wins/close wins + close losses) in one-score games for all teams (or a single team, if team != "All".
        '''
        url = f"https://www.pro-football-reference.com/years/{season}/games.htm"
        
        df = pd.read_html(url)[0].drop(['Unnamed: 5'], axis=1)
        df = df.drop_duplicates(keep=False)
        
    #    Adding point diff column and selecting one-score games
        df['PD'] = pd.to_numeric(df['Pts']) - pd.to_numeric(df['Pts.1'])
        close_games = df.loc[df['PD']<=8.0]
        
    #    Getting # of close games by team
        close_wins_by_team = close_games['Winner/tie'].value_counts()
        close_loss_by_team = close_games['Loser/tie'].value_counts()

    #    If only one or several teams are desired
        if team != 'All':
            close_wins_by_team = close_wins_by_team[team]
            close_loss_by_team = close_loss_by_team[team]
            
    #    Win % in one-score games by team
        close_game_win_pct = round((close_wins_by_team / (close_wins_by_team + close_loss_by_team)), 3)
                
    #    print('Wins in one-score games: \n', close_wins_by_team)
    #    print('Losses in one-score games:\n', close_loss_by_team)
    #    print('One-score game win % by team:\n', close_game_win_pct)
        
        return close_wins_by_team, close_loss_by_team, close_game_win_pct
            
            
    def getTOMargin(self, season=2020):
        '''
        Returns Turnover margin for all teams in a given season
        parameters:
            season - int or str (default 2020); season for which turnover stats are deisred
            
        returns:
            to_for - pandas.Series object; turnovers created (i.e. defensive turnovers) in a given season for each team
            to_against - pandas.Series object; turnovers committed (i.e. offensive turnovers) in a given season for each team
            to_diff - pandas.Series object; turnovers differential (to_for - to_diff) in a given season for each team
        '''
    #    reading in TOs for each team's defense (turnovers created) and dropping multi-index
        url_def = f"https://www.pro-football-reference.com/years/{season}/opp.htm"
        ddf = pd.read_html(url_def)[0]
        ddf.columns = [c[1] for c in ddf.columns]
        
    #    Getting Offenseive turnovers committed
        url_off = f"https://widgets.sports-reference.com/wg.fcgi?css=1&site=pfr&url=%2Fyears%2F{season}%2F&div=div_team_stats"
        odf = pd.read_html(url_off ,displayed_only=False)[0]
        odf.columns = [c[1] for c in odf.columns] # Getting rid of multi-index for cols
        odf = odf.iloc[0:32:]

    #    re-indexing for team labels
        ddf.index, odf.index = ddf['Tm'], odf['Tm']
        ddf = ddf.drop(['Avg Team', "Avg Tm/G", "League Total"], axis=0)

#        Calculating turnover differential for all teams
        to_for = ddf['TO']
        to_against = odf['TO']
        to_diff = to_for - to_against
        
        return to_for, to_against, to_diff
        
    def winLossPct(self, season):
        '''
        Returns total win/loss % for each team for a given season

        parameters:
            season - int or str (default 2020); season for which turnover stats are deisred
            
        returns:
            pandas.Series object containing total win-loss % for each NFL team
        
        '''
        print('Getting Win-Loss %s')
        standings_url = f'https://www.pro-football-reference.com/years/{season}/'
        dfs = pd.read_html(standings_url)

        df = pd.concat(dfs)
        divisions = ['NFC West', 'NFC South', 'NFC North', 'NFC East',
                     'AFC West', 'AFC South', 'AFC North', 'AFC East']

        
        df['Tm'] = df['Tm'].str.replace('*','')
        df['Tm'] = df['Tm'].str.replace('+','')
        df.index = df['Tm']
        df = df.drop(divisions, axis=0)

        
        return df['W-L%']

################################################################################################
################################################################################################
################################################################################################

def scatterPlot(df, col, season):
    '''
    Plots scatter plot of some metric (x-axis) vs win %
    '''
    print(f"Checking metric {col} for correlation with W-L%")
    plt.scatter(df[col],df['W-L%'])
    plt.xlabel(col)
    plt.ylabel('Win-Loss %')
    plt.title(f'2020 NFL {col} - Win/Loss%')

    plt.savefig(f'./plots/win-loss_vs_{col}-NFL-{season}.pdf')
    plt.clf()


def getSeasonData(season, save_csv=False):
    '''Returns key stats df for selected season'''
    to_for, to_against, to_diff = getTOMargin(season)
    w, l, pct = oneScoreRecord(season, 'All')
    pt_diff = getPtDiff(season)
    wl = winLossPct(season)

    #    Combining stats into one DataFrame
    df = pd.DataFrame(data = {'Pt Diff': pt_diff.sort_index(), 'W-L%': wl.sort_index(), 'TO For': to_for, 'TO Against': to_against, 'TD': to_diff, 'Wc': w, "Lc": l, "W-L% one score":pct}).astype(float)
    df = df.fillna(0)
    print(df)

    if save_csv:
        df.to_csv(f'testing_data_{season}.csv')#.head())
    
    f, ax = plt.subplots()
    ax.hist(df['Pt Diff'])
    ax.set_title(season)
    ax.set_xlabel('Point Differential')
#    plt.show()
    f.savefig(f'plots/pt_diff/pt_diff_{season}.pdf')
    
    return df

def potentialWinningPcts():
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

# Pt Diff, One-Score Record, Turnover Diff seem to be the most correlated (from what we've checked with W%
# Monte Carlo simulation for game prediction: https://en.wikipedia.org/wiki/Monte_Carlo_method
    
    getSeasonData(2020)
    potentialWinningPcts()
    
    for s in range(2020,2002,-1):
        getPtDiff(s)
    
