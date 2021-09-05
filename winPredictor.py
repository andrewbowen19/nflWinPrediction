# Script for predicting NFL Win totals
# Sharp article here: https://www.sharpfootballanalysis.com/betting/numbers-that-matter-for-predicting-nfl-win-totals-part-one/
#Scrapes Pro-Football Reference for data

import os
import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

def getDiff(season, return_teams=True):
    '''
    Scrapes PFR for point differential
    season: str or int, year to search for
    '''
    standings_url = f'https://www.pro-football-reference.com/years/{season}/'
    dfs = pd.read_html(standings_url)

    df = pd.concat(dfs)
#   Columns:  ['Tm', 'W', 'L', 'T', 'W-L%', 'PF', 'PA', 'PD', 'MoV', 'SoS', 'SRS',
#       'OSRS', 'DSRS']
    divisions = ['NFC West', 'NFC South', 'NFC North', 'NFC East',
                 'AFC West', 'AFC South', 'AFC North', 'AFC East']

#    Dropping standings footnotes (*/+) from the table
    df['Tm'] = df['Tm'].str.replace('*','')
    df['Tm'] = df['Tm'].str.replace('+','')
    
    df.index = df['Tm']
    df = df.drop(divisions, axis=0)
    df.to_csv(f'./standings/nfl_standings-{season}.csv')
    
#    Dropping team names as series index labels if desired (default True)
    if not return_teams:
        df.index = np.arange(0,len(df), 1)
    
#    print(df)
    
    return pd.to_numeric(df['PD'])

def oneScoreRecord(season, team='All'):
    '''
    Scrapes PRF Results
    season: str or int, NFL season search is desired for
    team: str, (default All), searches for all teams if
    '''
    url = f"https://www.pro-football-reference.com/years/{season}/games.htm"
    
    df = pd.read_html(url)[0].drop(['Unnamed: 5'], axis=1)
    df = df.drop_duplicates(keep=False)
    
#    Adding point diff column
    df['PD'] = pd.to_numeric(df['Pts']) - pd.to_numeric(df['Pts.1'])
    
#    Selecting one score games
    close_games = df.loc[df['PD']<=8.0]
    
#    Getting # of close games by team
    close_wins_by_team = close_games['Winner/tie'].value_counts()
    close_loss_by_team = close_games['Loser/tie'].value_counts()

#    Is user wants different team than every team
    if team != 'All':
        close_wins_by_team = close_wins_by_team[team]
        close_loss_by_team = close_loss_by_team[team]
        
#    Win % in one-score games by team
#    else:
    close_game_win_pct = round((close_wins_by_team / (close_wins_by_team + close_loss_by_team)), 3)
            
#    print('Wins in one-score games: \n', close_wins_by_team)
#    print('Losses in one-score games:\n', close_loss_by_team)
#    print('One-score game win % by team:\n', close_game_win_pct)
    
    return close_wins_by_team, close_loss_by_team, close_game_win_pct
        
        
def getTOMargin(season):
    '''
    Returns TO margin for a team
    season: int or str, season for which turnover stats are deisred
    '''
#    reading in TOs for each team's defense (turnovers created)
    url_def = f"https://www.pro-football-reference.com/years/{season}/opp.htm"
    
    ddf = pd.read_html(url_def)[0]
    ddf.columns = [c[1] for c in ddf.columns]
    
#    Getting Offenseive turnovers
    url_off = f"https://widgets.sports-reference.com/wg.fcgi?css=1&site=pfr&url=%2Fyears%2F{season}%2F&div=div_team_stats"
    odf = pd.read_html(url_off ,displayed_only=False)[0]#.reindex
    odf.columns = [c[1] for c in odf.columns] # Re-naming columns from these weird tuples
    odf = odf.iloc[0:32:]

    
#    re-indexing for team labels
    ddf.index, odf.index = ddf['Tm'], odf['Tm']
    ddf = ddf.drop(['Avg Team', "Avg Tm/G", "League Total"], axis=0)
    
    to_for = ddf['TO'] # Defensive turnovers
    to_against = odf['TO']
    
    to_diff = to_for - to_against
#    print(to_diff)
    
    
    return to_for, to_against, to_diff
    
def winLossPct(season):
    '''
    Returns total win/loss % for each team for a given season
    '''
    print('Getting Win-Loss %s')
    standings_url = f'https://www.pro-football-reference.com/years/{season}/'
    dfs = pd.read_html(standings_url)
#    print(dfs[0])
#    print('#################################')
#    print(dfs[1])

    df = pd.concat(dfs)
    divisions = ['NFC West', 'NFC South', 'NFC North', 'NFC East',
                 'AFC West', 'AFC South', 'AFC North', 'AFC East']

    
    df['Tm'] = df['Tm'].str.replace('*','')
    df['Tm'] = df['Tm'].str.replace('+','')
    df.index = df['Tm']
    df = df.drop(divisions, axis=0)

    
    return df['W-L%']
    

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

def checkCorrs():
    '''
    Returns df of correlation with Win % for each season dating back to 2002
    '''
    with open('NFL-Win%-Stats.txt', 'w') as f:
        corrs = {'Season':[], 'Pt Diff':[], 'TO For':[],'TO Against':[], 'TD':[], 'Wc':[], 'Lc':[],'W-L% one score':[]}
        p_vals = {'Season':[], 'Pt Diff':[],'TO For':[],'TO Against':[], 'TD':[], 'Wc':[], 'Lc':[],'W-L% one score':[]}
        for s in range(2020, 2002, -1):
            print("######################################")
            print(f'Season: {s}')
            f.write(str(s) + '\n')
            corrs['Season'].append(s)
#            Grabbing stats for that season
            to_for, to_against, to_diff = getTOMargin(s)
            w, l, pct = oneScoreRecord(s, 'All')
            pt_diff = getDiff(s)
            wl = winLossPct(s)

        #    Combining stats into one DataFrame
            df = pd.DataFrame(data = {'Pt Diff': pt_diff.sort_index(), 'W-L%': wl.sort_index(), 'TO For': to_for, 'TO Against': to_against, 'TD': to_diff, 'Wc': w, "Lc": l, "W-L% one score":pct}).astype(float)
            df = df.fillna(0)
            print(df.head())
            
            df.to_csv(os.path.join('.','season_stats', f'nfl_stats_{s}.csv'))

            
    #        Doing it for each stat column in our DataFrame
            for c in df.columns:
                if c != "W-L%":
                    print(f"Checking metric {c} for correlation with W-L%")
                    scatterPlot(df, c, s)
                    
    #                Printing out correlation and writing to a txt file
                    corr, p = pearsonr(df[c], df['W-L%'])
                    print('Correlation with win %: ', corr)
                    print('p-value with Win %', p)
                    print('Creating Figure...')
                    
                    corrs[c].append(corr)
                    
#                    Write that sucka
                    
                    f.write(f'Stat: {c}  \n')
                    f.write(f'Correlation of {c} with win %: {corr}\n')
                    f.write(f'p-value with Win %: {p}\n')
                    print('-------------------------------------------')
#                    f.write(f'Creating Figure...')
            f.write('-------------------------------------------\n')
                    
#    print(corrs)
    cf = pd.DataFrame(corrs)
    print(cf)
    return cf

def getSeasonData(season, save_csv=False):
    '''Returns key stats df for selected season'''
    to_for, to_against, to_diff = getTOMargin(season)
    w, l, pct = oneScoreRecord(season, 'All')
    pt_diff = getDiff(season)
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
    Spits out list of all possible records and winning % with  17-game schedule
    '''
    w=0
    l = 17
    records = {}
    while w <= 17 and l >= 0:
        win_pct = w/(w + l)
        records[f'{w}-{l}'] = round(win_pct, 3)
        
        w += 1
        l -= 1
        
    print(records)
        
    
    


#Want to see how these values (TD, PD, Close-game win %) vary season to season


if __name__ == "__main__":

# Pt Diff, One-Score Record, Turnover Diff seem to be the most correlated (from what we've checked with W%
# Monte Carlo simulation for game prediction: https://en.wikipedia.org/wiki/Monte_Carlo_method
    
    getSeasonData(2020)
    potentialWinningPcts()
    
    for s in range(2020,2002,-1):
        getDiff(s)
    
