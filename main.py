from utility.api import alpaca_data
import os
import websocket
import json
import rel


# api = alpaca_data()
# print(api.list_positions())

# socket time
url = f'{os.environ.get("WSS_BASE_URL")}quotes/price?apikey={os.environ.get("TWELVEDATA_KEY")}'

def on_message(ws, message):
    print("THIS IS TRIGGERED EVERY TIME WE GET A MESSAGE FROM THE SOCKET")
    loaded = json.loads(message)
    if(loaded["price"]):
        print(loaded["price"])

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    ws.send(json.dumps({
        "action": "subscribe",
        "params": {
            "symbols": "BTC/USD"
        }
    }))
    print("Opened connection")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close)

    ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()
