from utility.api import alpaca_data
from utility.actions import delineator
import requests, os, websocket, json, rel

class BlackBox:
    # sets up initial equity/liquid cash amount
    money_ceiling = 1000000000
    liquid_cash = 1000000000 # <- should subtract from this based on the initial data points in bagholder_log
    url = f'{os.environ.get("WSS_BASE_URL")}quotes/price?apikey={os.environ.get("TWELVEDATA_KEY")}'
    trail = []
    bagholder_log = [
        # { (structure example)
        #   symbol: string
        #   data: [
        #       {
        #           date_purchased: timestamp
        #           date_sold: timestamp
        #           price: double/int/whatever
        #           amount: double/int/whatever
        #           held: boolean
        #       }
        #   ]
        # }
        {
            "symbol": "BTC/USD",
            "data": [
                {
                    "date_purchased": "",
                    "date_sold": "",
                    "price": 36988.1,
                    "amount": 1,
                    "held": True
                }
            ]
        },
    ]
    data = [
            {
                "limit": 10,
                "avg": 0,
                "low": 0,
                "high": 0
            },
            {
                "limit": 20,
                "avg": 0,
                "low": 0,
                "high": 0
            },
            {
                "limit": 30,
                "avg": 0,
                "low": 0,
                "high": 0
            },
        ]
    # api = alpaca_data()

    def  __init__(self):
        # set close, medium, far moving average day ranges
        self.data[0]["limit"], self.data[1]["limit"], self.data[2]["limit"] = 50, 100, 200
        self.update_equity(self.holdings_sum(), 'sub')
        self.run()  

    def holdings_sum(self):
        amt = 0
        for entry in self.bagholder_log:
            for each in entry["data"]:
                amt += each["price"]
        
    # simple method to update cash without directly accessing the variable so there are less points of failure. Maybe.
    def update_equity(self, action, amt):
        if(action == 'add'):
            self.liquid_cash += amt
        if(action == 'sub'):
            self.liquid_cash -= amt

    def run(self):
        data_points = requests.get(f'{os.environ.get("BASE_URL")}time_series?symbol=BTC/USD&outputsize=100&interval=1day&apikey={os.environ.get("TWELVEDATA_KEY")}')
        serialized = data_points.json()
        for data in serialized["values"]:
            self.on_message(None, data)

        print(self.bagholder_log)
        # ws = websocket.WebSocketApp(url,
        #     on_open=on_open,
        #     on_message=on_message,
        #     on_error=on_error,
        #     on_close=on_close)

        # ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
        # rel.signal(2, rel.abort)  # Keyboard Interrupt
        # rel.dispatch()

    # listeners for websocket
    def on_message(self, ws, message):
        print(message)
        # delineator(json.loads(message))
        # feeds all inputs into market operations per tick
        delineator(message,
            {
                "max": self.money_ceiling,
                "cash": self.liquid_cash,
                "trail": self.trail,
                "history": self.bagholder_log,
                "moving": self.data
            }
        )

    def on_error(self, ws, error):
        print(error)

    def on_close(ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(self, ws):
        ws.send(json.dumps({
            "action": "subscribe",
            "params": {
                "symbols": "BTC/USD"
            }
        }))
        print("Opened connection")

if __name__ == "__main__":
    BlackBox()