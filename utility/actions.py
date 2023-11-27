# import alpaca_trade_api as alpaca
from .fake_data import fake, get_fake
import pytz
from datetime import datetime
tz = pytz.timezone('America/New_York')

def delineator(data):
    fake(data)
    print(get_fake())
    
    # print (f'{datetime.fromtimestamp(data["timestamp"], tz).isoformat()},{data["price"]}')
