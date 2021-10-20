# Script to figure out how to get prediction on Turnover Differential for a season

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import pymc3 as pm


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
    
#    Writing to files
    
    odf.to_csv(os.path.join('..', 'data', 'stats', f'offenseStats-{season}.csv'))
    ddf.to_csv(os.path.join('..', 'data', 'stats',f'defenseStats-{season}.csv'))
    
    
    to_for = ddf['TO'] # Defensive turnovers
    to_against = odf['TO']
    
    to_diff = to_for - to_against
#    print(to_diff)
    to_diff = to_diff.rename(str(season))
    
    return to_for, to_against, to_diff

def plotHistoricalTODiff(plot_dist=True):
    '''
    Plots distribution of NFL Turnover differentials for seasons 2002-2020
    They follow a decently symmetrical/normal(?) distribution
    '''
    diffs = []
    
    for s in range(2020,2002,-1):
        
        tof, toa, td = getTOMargin(s)
#        print(tof, toa, td)
        diffs.append(td)
        
    print(diffs)
    df = pd.concat(diffs, axis=1)
    print(df)
    
    if plot_dist:
        f,ax = plt.subplots()
        ax.hist(df, bins=len(np.unique(df)))
        plt.xlabel('Turnover diff 2002 - 2020')
        plt.show()
    return df
    
########## Markov Chain Implementation ###########

#Bayesian Stats article: https://en.wikipedia.org/wiki/Posterior_probability


if __name__  == '__main__':
    print('Playing around with MCMC implementation')
    df = plotHistoricalTODiff(False)
    
#    Setting up pymc3 model
#    with pm.Model():
#
#        x = pm.Normal('x', mu=np.mean(df), sigma=np.std(df))
#        y = pm.Normal('y', mu=np.mean(df), sigma=np.std(df), observed=list(df))
#        r = x.random(size=500)
#        print(r)
#
#        plt.hist(r)
#        print(y, type(y))
#        plt.show()

