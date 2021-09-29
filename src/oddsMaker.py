# Script to retrieve betting odds for NFL games via the odds-api
# Docs here: https://the-odds-api.com/liveapi/guides/v4/#overview

import pandas as pd
import requests
import os
import json
import numpy as np
import datetime as dt

api_key = "b13e7359d6aa2d094b2b3afe2e31c110"
url = f"https://api.the-odds-api.com/v4/sports?apiKey={api_key}"
nfl_url = f"https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/?regions=us&oddsFormat=american&apiKey={api_key}"

# ##### Saving our API Calls
#r = requests.get(nfl_url)
#
###Writing reqpsonse to csv to preserve API calls
#for i, v in enumerate(r.json()):
#    df = pd.DataFrame(v)
#    if len(df)> 1:
#        df.to_csv(f'my_odds/odds-{i}.csv')
#################################################


def getBestOdds(df):
    '''
    Pulls best odds from Odds-API response
    '''
    away_team = df['away_team'].iloc[1]
    home_team = df['home_team'].iloc[1]
    print(f'Selecting best odds for matchup: {away_team} @ {home_team}')
    print(df.head())
    
    odds = {away_team: [], home_team: [], 'oddsmaker':[]}
    
#    Stripping API response for odds for the matchup
    for p in df['bookmakers']:
        d = json.loads(p.replace("\'", "\""))
#        print(d['title'])
        odds['oddsmaker'].append(d['title'])
        for team in d['markets'][0]['outcomes']:
            
            if team['name']==away_team:
                away_odds = team['price']
                odds[away_team].append(away_odds)
            elif team['name']==home_team:
                home_odds = team['price']
                odds[home_team].append(home_odds)
                
        print(f'Away odds {away_team}: {away_odds}')
        print(f'Home odds {home_team}: {home_odds}')
        
    df = pd.DataFrame(odds)
    print(df)
#    Pulling best odds for home and away team of this matchup
#    Home team odds < 0, so the max will be best -- same for away team
    best_away_odds = np.max(odds[away_team])
    best_home_odds = np.max(odds[home_team])
    best_away_oddsmaker = df['oddsmaker'].iloc[np.argmax(df[away_team])]
    best_home_oddsmaker = df['oddsmaker'].iloc[np.argmax(df[home_team])]
#    print(best_away_oddsmaker, best_home_oddsmaker)
    
    
    print("###############################################")
    return away_team, home_team, best_away_odds, best_home_odds, best_away_oddsmaker, best_home_oddsmaker

def moneylineArbitrage(odds_favorite, odds_dog, bet = 10):
    '''
    Determines whether a set of two american style odds produce an arbitrage
    https://www.sportsbettingdime.com/guides/strategy/arbitrage-betting/
    odds_favorite: int < 0, odds for the favored team (american style; i.e. -390)
    odds_dog: int > 0, american-style (e.g. +480) odds for the underdog team
    bet: int, default 10. Input bet amount (one unit)
    '''
#    Def need to check my math here
#    if odds_favorite < 0:
    payout_fav = (100 * bet) / abs(odds_favorite)
    print(f'Favored team payout on ${bet} bet: {payout_fav}')

#    if odds_dog < 0:
    payout_dog = (odds_dog * bet) / 100
    print(f'Underdog payout on ${bet} bet: {payout_dog}')
    
    
    if (payout_dog + payout_fav) > (2*bet):
#        print(f'Total Payout by splitting {2*bet} two-ways: {payout_fav + payout_dog}')
        print('Arbitrage Detected')
        
    else:
#        print(f'Total Payout by splitting {2*bet} two-ways: {payout_fav + payout_dog}')
        print('No arbitrage here.')
    
    

#Looping through matchups
if __name__=='__main__':

    odds_path = os.path.join('.', 'my_odds')
    week1 = dt.datetime(2021, 9 , 12, 11, 59, 59, 000000)
    for f in os.listdir(odds_path):  # Will swap this out for API calls
    
        dat = pd.read_csv(os.path.join(odds_path, f), header=0)
        dat = dat.drop(['Unnamed: 0'], axis=1)
        
     
        away, home, a_odds, h_odds, a_book, h_book = getBestOdds(dat)
        
        print(f'Best odds for {away}: {a_odds}')
        print(f'Best odds for {home}: {h_odds}')
        
        if h_odds < 0:
            moneylineArbitrage(h_odds, a_odds, 10)
        
        elif h_odds > 0:
            moneylineArbitrage(a_odds, h_odds, 10)
#        if (a_odds + h_odds) > 0:
#            print('Arbitrage detected!')
#            print(f'Away book w/ arbitrage {a_book} | Home book w/ arbitrage: {h_book}')
#        else:
#            print('No arbitrage detected.')
            
#            Would like the script to also spit out the
            
            
