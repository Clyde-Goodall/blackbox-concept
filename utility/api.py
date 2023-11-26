import os
from os.path import join, dirname
from dotenv import load_dotenv, find_dotenv
import requests, json
import alpaca_trade_api as alpaca
import pandas as pd
import numpy as np
# from scipy.signal import argrelextrema

env_loc = find_dotenv()
load_dotenv(env_loc)

"""
valid market ticker required.
supported intervals 1min, 5min, 15min, 30min, 45min, 1h, 2h, 4h, 1day, 1week, 1month
flag to return json or not

# eg | thing = time_series('MSFT', '2h')
"""
def time_series(ticker, interval, json=True):
    """
    this interpolates the param 'ticker' into the string so that you can easily spit out a
    formatted string for the symbol you want.
    I'll add time frequency as a param too.
    """
    # print(f'{os.environ.get("BASE_URL")}/time_series?symbol={ticker}&interval={interval}&apikey={os.environ.get("TWELVEDATA_KEY")}')
    try:
        res = requests.get(
            f'{os.environ.get("BASE_URL")}/time_series?symbol={ticker}&interval={interval}&apikey={os.environ.get("TWELVEDATA_KEY")}'
        )
        res_json = res.json()
        if(res_json): return res_json
        return res
    except Exception:
        print(Exception)

"""
portfolio holdings output
this is an api object, it can be used to call whatever methods fro the alpaca_trade_api library,
not just portfolio content
"""
def alpaca_data():
    print(os.environ.get("ALPACA_KEY"))
    return alpaca.REST(os.environ.get("ALPACA_KEY"), os.environ.get("ALPACA_SECRET"), os.environ.get("ALPACA_URL")
)
