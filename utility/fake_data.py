from .status import Status

def logg(message, status="WARNING"):
    color_map = {
        "OK": "\033[92m",
        "ERROR": "\033[94m",
        "UNSUCCESSFUL": "\033[91m",
        "WARNING": "\033[93m",
    }
    print(f'{message}')

# pulls in moving average/high/low tracker and buy/sell conditions to be referenced in the on_message websocket listener
def fake(incoming, inputs):
    # destrucrure the inputs a little bit so it's not obnoxious
    trail = inputs["trail"]
    data = inputs["moving"]
    # for tenporary, non-websocket tests. Maybe should be flagged so we don't have to alter.
    incoming["price"] = (float(incoming["low"]) + float(incoming["high"]) + float(incoming["open"]) + float(incoming["close"]))/4
    incoming["timestamp"] = incoming["datetime"]
    incoming["symbol"] = "BTC/USD"
    trail.append(incoming["price"])
    # update all time range values
    for entry in data:
        if(len(trail) < entry["limit"]):
            entry["low"] = min(trail)
            entry["high"] = max(trail)
            entry["avg"] = sum(trail)/len(trail)
            continue

        # updates values for each time range
        entry["avg"] = sum(trail[(entry["limit"]-1):])/len(trail[(entry["limit"]-1):])
        entry["low"] = min(trail[(entry["limit"]-1):])
        entry["high"] = max(trail[(entry["limit"]-1):])
    print( f'Recalculated low/high and Moving avgs.')
    print(data[0])
    print(data[1])
    print(data[2])

    for entry in data:
         market_action_trigger_conditions(incoming, inputs, entry)
        # market actions
        
"""
Market Action Trigger Conditions:
    Controller for market actions based on output from P/L Calculators
    Negative return value points to trigger_buy
    Positive return value points to trigger_sell
"""
def market_action_trigger_conditions(incoming, inputs, entry):
    liquid_temp = inputs["cash"]
    if(round(incoming["price"]) >= round(entry["low"]) 
       and round(incoming["price"]) <= round(entry["high"])):
        p_l = profit_loss_calc(incoming, inputs)
        logg("WARNING", f'P/L: {p_l}')
        if(p_l == 0): return
        if(p_l < 0):
            trigger_buy(incoming, inputs)
        if(p_l > 0):
            trigger_sell(incoming, inputs)
            
    logg("OK", f'Cash before iteration: {liquid_temp}. Cash after: {liquid_temp}')

"""
P/L Calculator:
    Returns whether P/L is positive or negative. 
"""
def profit_loss_calc(incoming, inputs):
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
    logg("WARNING", found)
    if(not found): 
        inputs["hstory"].append({
            "symbol": incoming["symbol"],
            "data":[]
        })
        found = inputs["history"][-1]
        logg("WARNING", f'Added symbol "{incoming["symbol"]}" to track for market actions')
    for i in range(amt):
        found["data"].append({
            "date_purchased": incoming["timestamp"],
            "price": incoming["price"],
            "amount": amt,
            "held": True
        })
        inputs["cash"] -= incoming["price"]
    logg("OK", f'purchased {amt} shares of {incoming["symbol"]}')

    return Status.OK

"""
Trigger Sell:
    Explanation of logic should go here
"""
def trigger_sell(incoming, inputs, amt=1):
    found = next((entry for entry in inputs["history"] if entry["symbol"] == incoming["symbol"]), None)
    # if it's trying to sell securities we don't own something is fucky wucky
    if(not found): 
        logg("ERROR", f'Attempted sale for {incoming["symbol"]}, but the account is currently not holding any ')
        return
    if(amt > len(found["data"])): 
            return Status.UNSUCCESSFUL
    for i in range(amt):
        found["data"][i]["held"] = False
        found["data"][i]["date_sold"] = incoming["timestamp"]

        inputs["cash"] += incoming["price"]
    logg("OK", f'sold {amt} shares of {incoming["symbol"]}')

    return Status.OK