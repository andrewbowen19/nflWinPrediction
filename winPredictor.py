# Script for predicting NFL Win totals
# Sharp article here: https://www.sharpfootballanalysis.com/betting/numbers-that-matter-for-predicting-nfl-win-totals-part-one/
#Scrapes Pro-Football Reference for data

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
    
#    Dropping team names as series index labels if desired (default True)
    if not return_teams:
        df.index = np.arange(0,len(df), 1)
    
#    print(df)
    
    return df['PD']

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
    url_def = f"https://www.pro-football-reference.com/years/{season}/opp.htm#team_stats"
    
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

    
if __name__ == "__main__":

# Pt Diff, One-Score Record, Turnover Diff seem to be the most correlated (from what we've checked with W%
# Monte Carlo simulation for game prediction: https://en.wikipedia.org/wiki/Monte_Carlo_method

    cf = checkCorrs()
    
    plt.scatter(cf['W-L% one score'], cf['Pt Diff'])
    plt.xlabel('One-score game Win %')
    plt.ylabel('Pt Diff')
    
    plt.show()
