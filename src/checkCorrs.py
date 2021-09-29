# Script to check correlation of different NFL team statistics with overall winning %
# Data provided by scraping pro-football-reference.com

import os
import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from winPredictor import winLossPct, getPtDiff, oneScoreRecord, getTOMargin


def checkCorrs():
    '''
    Returns df of correlation of different statsistics (scraped from PFR) with Win % for each season dating back to 2002
    
    As expected, the statistics with the consistently highest correlations
    '''
    with open('NFL-Win%-Stats.txt', 'w') as f:
        corrs = {'Season': [], 'Pt Diff': [], 'TO For': [],'TO Against': [], 'TD': [], 'Wc': [], 'Lc': [],'W-L% one score': []}
        p_vals = {'Season': [], 'Pt Diff': [],'TO For': [],'TO Against': [], 'TD': [], 'Wc': [], 'Lc': [],'W-L% one score':[]}
        for s in range(2020, 2002, -1):
            print("######################################")
            print(f'Season: {s}')
            f.write(str(s) + '\n')
            corrs['Season'].append(s)
#            Grabbing stats for that season
            to_for, to_against, to_diff = getTOMargin(s)
            w, l, pct = oneScoreRecord(s, 'All')
            pt_diff = getPtDiff(s)
            wl = winLossPct(s)

        #    Combining stats into one DataFrame
            df = pd.DataFrame(data = {'Pt Diff': pt_diff.sort_index(), 'W-L%': wl.sort_index(), 'TO For': to_for, 'TO Against': to_against, 'TD': to_diff, 'Wc': w, "Lc": l, "W-L% one score": pct}).astype(float)
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
