import json
from datetime import datetime
def logg(status="WARNING", message=""):
    color_map = {
        "OK": "\033[92m",
        "ERROR": "\033[94m",
        "UNSUCCESSFUL": "\033[91m",
        "WARNING": "\033[93m",
    }
    date = datetime.today().strftime('%Y-%m-%d %H:%M:%s')
    print(f'[{date}]{message}')

# pulls in moving average/high/low tracker and buy/sell conditions to be referenced in the on_message websocket listener
def fake(incoming, inputs, config):
    if("price" not in incoming and config["realtime"]): return
    # destrucrure the inputs a little bit so it's not obnoxious
    trail = inputs["trail"]
    data = inputs["moving"]
    if(not config["realtime"]):
        incoming["price"] = (float(incoming["low"]) + float(incoming["high"]) + float(incoming["open"]) + float(incoming["close"]))/4
    trail.append(incoming["price"])
    # print(trail)
    # update all time range values
    for entry in data:
        if(len(trail) < entry["limit"] and len(trail) > 0):
            entry["low"] = min(trail)
            entry["high"] = max(trail)
            entry["avg"] = sum(trail)/len(trail)
            continue

        # updates values for each time range
        if(len(trail) > 0):
            entry["avg"] = sum(trail[(entry["limit"]-1):])/len(trail[(entry["limit"]-1):])
            entry["low"] = min(trail[(entry["limit"]-1):])
            entry["high"] = max(trail[(entry["limit"]-1):])
    logg( f'Recalculated low/high and Moving avgs.')

    for entry in data:
         market_action_trigger_conditions(incoming, inputs, entry)
    logg(f'P/L: {profit_loss_calc(incoming, inputs)}')
        
"""
Market Action Trigger Conditions:
    Controller for market actions based on output from P/L Calculators
    Negative return value points to trigger_buy
    Positive return value points to trigger_sell
"""
def market_action_trigger_conditions(incoming, inputs, entry):
    liquid_temp = inputs["cash"]
    if("price" not in incoming): return
    if(round(incoming["price"]) >= round(entry["low"]) 
       and round(incoming["price"]) <= round(entry["high"])):
        p_l = profit_loss_calc(incoming, inputs)
        date = ""
        if("timestamp" in incoming):
            date = incoming["timestamp"]
        else:
            date = incoming["datetime"]
        inputs["live"].append({
            "p_l": p_l,
            "date": date
        })
        if(p_l == 0): return
        if(p_l < 0):
            trigger_buy(incoming, inputs)
        if(p_l > 0 and len(inputs["trail"]) >= 10 ):
            trigger_sell(incoming, inputs)

"""
P/L Calculator:
    Returns whether P/L is positive or negative. 
"""
def profit_loss_calc(incoming, inputs): 
    if(incoming["symbol"]):
        found = next((entry for entry in inputs["history"] if entry["symbol"] == incoming["symbol"]), None)
    if(not found): 
        logg("OK", f'Couldn\'t find entry to run P/L on.')
        return
    total_amt = 0
    total_value = 0
    for order in found["data"]:
        # only counts open positions
        if(order["held"]):
            total_amt += 1
            total_value += incoming["price"]
    if(total_amt == 0): return 0
    avg = total_value/total_amt
    avg += inputs["cash"]

    return avg - inputs["max"]
    
# alpaca portfolio/rebalance actions
"""
Trigger Buy:
    Explanation of logic should go here
"""
def trigger_buy(incoming, inputs, amt=1):
    found = next((entry for entry in inputs["history"] if entry["symbol"] == incoming["symbol"]), None)
    if(not found): 
        inputs["hstory"].append({
            "symbol": incoming["symbol"],
            "data":[]
        })
        found = inputs["history"][-1]
        logg("", f'Added symbol "{incoming["symbol"]}" to track for market actions')
    for i in range(amt):
        date = ""
        if("timestamp" in incoming):
            date = incoming["timestamp"]
        else:
            date = incoming["datetime"]
        
        found["data"].append({
            "date_purchased": date,
            "price": incoming["price"],
            "amount": amt,
            "held": True
        })
        inputs["cash"] -= incoming["price"]
    logg("OK", f'purchased {amt} shares of {incoming["symbol"]}')


"""
Trigger Sell:
    Explanation of logic should go here
"""
def trigger_sell(incoming, inputs, amt=1):
    found = next((entry for entry in inputs["history"] if entry["symbol"] == incoming["symbol"]), None)
    # if it's trying to sell securities we don't own something is fucky wucky
    p_l = profit_loss_calc(incoming, inputs)
    p_l_percent = p_l / incoming["price"] * 100
    shares_amt_to_sell = 0
    if(p_l_percent > 20 and p_l_percent < 50):
        shares_amt_to_sell = .1
    elif(p_l_percent >= 50 and p_l_percent < 90):
        shares_amt_to_sell = .5
    elif(p_l_percent >= 90):
        shares_amt_to_sell = .8
    logg(found)
    # multiplies share sales amoutn by how many purchased shares in the given found entry's values
    int_shares_to_sell = int(shares_amt_to_sell * 100 * len(found["data"]))
    if(int_shares_to_sell == 0): return

    if(not found): 
        logg("ERROR", f'Attempted sale for {incoming["symbol"]}, but the account is currently not holding any ')
        return
    if(amt > len(found["data"])): 
            return "oopsie"
    for i in range(int_shares_to_sell):
        found["data"][i]["held"] = False
        if("datetime" in incoming):
            found["data"][i]["date_sold"] = incoming["datetime"]
        else:
            found["data"][i]["date_sold"] = incoming["timestamp"]
        inputs["cash"] += incoming["price"]
    logg("OK", f'sold {int_shares_to_sell} shares of {incoming["symbol"]}')
