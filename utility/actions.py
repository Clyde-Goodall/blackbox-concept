# import alpaca_trade_api as alpaca
import pytz
from datetime import datetime
tz = pytz.timezone('America/New_York')

def delineator(data):
    print (f'{datetime.fromtimestamp(data["timestamp"], tz).isoformat()},{data["price"]}')
# alpaca portfolio/rebalance actions

def triggered_buy(ticker, amt, order_type="mkt"):
    # todo
    return

def triggered_sell(ticker, amt, order_type="mkt"):
    # todo
    return