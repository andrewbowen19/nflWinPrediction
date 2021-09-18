# Script to format data for Play-by-play (pbp) analysis of NFL Games
# Scrapes pbp data from pro-football ref

import pandas as pd
import numpy as np

sample_url = "https://widgets.sports-reference.com/wg.fcgi?css=1&site=pfr&url=%2Fboxscores%2F202109090tam.htm&div=div_pbp"


#KC-Browns embed link:
#script src="https://widgets.sports-reference.com/wg.fcgi?css=1&site=pfr&url=%2Fboxscores%2F202109120kan.htm&div=div_pbp


df = pd.read_html(sample_url, header=0, displayed_only=True)[0]

print(len(df))

print(df)
print(df.columns)


