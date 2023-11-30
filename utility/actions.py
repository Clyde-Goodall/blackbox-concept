# import alpaca_trade_api as alpaca
from .fake_data import fake
from .status import Status
import pytz
from datetime import datetime
tz = pytz.timezone('America/New_York')

def delineator(data, inputs):
    fake(data, inputs)
    
    # print (f'{datetime.fromtimestamp(data["timestamp"], tz).isoformat()},{data["price"]}')

