from utility.api import alpaca_data
from ascii import startup_banner
from utility.actions import delineator
import requests, os, websocket, json, rel
import seaborn as sns
import pandas as pd

class BlackBox:
    config: dict
    # sets up initial equity/liquid cash amount
    money_ceiling = 1000000000
    liquid_cash = 1000000000 # <- should subtract from this based on the initial data points in bagholder_log
    url = f'{os.environ.get("WSS_BASE_URL")}quotes/price?apikey={os.environ.get("TWELVEDATA_KEY")}'
    trail = []
    p_l_live = []
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
                    "date_purchased": "2023-11-30",
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

    def  __init__(self, config):
        startup_banner()
        self.config = config
        # set close, medium, far moving average day ranges
        self.data[0]["limit"], self.data[1]["limit"], self.data[2]["limit"] = config["moving_averages"][0], config["moving_averages"][1], config["moving_averages"][2]
        self.update_equity(self.holdings_sum(), 'sub')
        self.run()  

    def holdings_sum(self):
        amt = 0
        for entry in self.bagholder_log:
            for each in entry["data"]:
                amt += each["price"]
        return amt
        
    # simple method to update cash without directly accessing the variable so there are less points of failure. Maybe.
    def update_equity(self, amt, action):
        if(action == 'add'):
            self.liquid_cash += amt
        if(action == 'sub'):
            self.liquid_cash -= amt

    def run(self):
        if(not self.config["realtime"]):
            data_points = requests.get(f'{os.environ.get("BASE_URL")}time_series?symbol={self.config["tickers"]}&outputsize={self.config["history"]}&interval={self.config["interval"]}&apikey={os.environ.get("TWELVEDATA_KEY")}')
            serialized = data_points.json()
            for data in serialized["values"]:
                data["symbol"] = serialized["meta"]["symbol"]
                self.on_message(None, data)

            # print(self.bagholder_log)
            print(self.p_l_live)
            iter = 0
            for symbol in self.bagholder_log:
                print(f'{symbol["symbol"]} chart written to file')
                frame = pd.DataFrame(self.p_l_live)
                plot = sns.lineplot(data=frame, x="date", y="p_l", errorbar=None)
                fig = plot.get_figure()
                fig.savefig(f'./chart-output/{symbol["symbol"].replace("/", "")}chart-{iter}.png')
                iter += 1
            return
        
        ws = websocket.WebSocketApp(self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close)

        ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
        rel.signal(2, rel.abort)  # Keyboard Interrupt
        rel.dispatch()

        # generate chart of P&L at the end of a batch simulation
        

    # listeners for websocket
    def on_message(self, ws, message):
        # delineator(json.loads(message))
        # feeds all inputs into market operations per tick
        actual_data: dict
        if(self.config["realtime"]):
            actual_data = json.loads(message)
        else:
            actual_data = message
        delineator(
            actual_data, 
            {
                "max": self.money_ceiling,
                "cash": self.liquid_cash,
                "trail": self.trail,
                "history": self.bagholder_log,
                "moving": self.data,
                "trail": self.trail,
                "live": self.p_l_live
            },
            self.config
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
        print("Waiting for first tick............")

if __name__ == "__main__":
    BlackBox({
        "realtime": True,
        "moving_averages": [50, 100, 200],
        "history": 500,
        "interval": "1day",
        "tickers": "BTC/USD" # <- separate multiple by comma, no space
    })