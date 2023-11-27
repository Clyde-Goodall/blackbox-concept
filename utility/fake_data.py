from .status import Status

trail = []
money_ceiling = 1000000000
counterfeit_money = 1000000000
counterfeit_money -= 36988.1
bagholder_log = [
    # {
    #   symbol: string
    #   data: [
    #   {
    #       date_purchased
    #       date_sold
    #       price
    #       amount
    #       held (bool)
    #   }
    # ]

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

def logg(message, status="WARNING"):
    color_map = {
        "OK": "\033[92m",
        "ERROR": "\033[94m",
        "UNSUCCESSFUL": "\033[91m",
        "WARNING": "\033[93m",
    }
    print(f'{color_map[status]}[*] \033[0m / {message}')

def get_fake():
    return data

# pulls in moving average/high/low tracker and buy/sell conditions to be referenced in the on_message websocket listener
def fake(input):
    trail.append(input["price"])
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
         market_action_trigger_conditions(input, entry)
        # market actions
        

# actually triggers market sales given the conditions are right, using P/L calc
def market_action_trigger_conditions(input, entry):
    liquid_temp = counterfeit_money
    if(round(input["price"]) == round(entry["low"])):
        p_l = profit_loss_calc(input)
        logg("WARNING", f'P/L: {p_l}')
        if(p_l < 0):
            trigger_buy(input)
        if(p_l > 0):
            trigger_sell(input)
            
    logg("OK", f'Cash before iteration: {liquid_temp}. Cash after: {liquid_temp}')

# returns whether P/L is positive or negative. 
def profit_loss_calc(input):
    found = next((entry for entry in bagholder_log if entry["symbol"] == input["symbol"]), None)
    if(not found): 
        logg("OK", f'Couldn\'t find entry to run P/L on.')
        return
    total_amt = 0
    total_value = 0
    for order in found["data"]:
        # only counts open positions
        if(order["held"]):
            total_amt += 1
            total_value += input["price"]
    avg = total_value/total_amt
    avg += counterfeit_money

    return avg - money_ceiling
    
# alpaca portfolio/rebalance actions

def trigger_buy(input, amt=1):
    found = next((entry for entry in bagholder_log if entry["symbol"] == input["symbol"]), None)
    logg("WARNING", found)
    if(not found): 
        bagholder_log.append({
            "symbol": input["symbol"],
            "data":[]
        })
        found = bagholder_log[-1]
        logg("WARNING", f'Added symbol "{input["symbol"]}" to track for market actions')
    for i in range(amt):
        found["data"].append({
            "date_purchased": input["timestamp"],
            "price": input["price"],
            "amount": amt,
            "held": True
        })
        equity -= data["price"]
    logg("OK", f'purchased {amt} shares of {input["symbol"]}')

    return Status.OK

def trigger_sell(input, amt=1):
    found = next((entry for entry in bagholder_log if entry["symbol"] == input["symbol"]), None)
    # if it's trying to sell securities we don't own something is fucky wucky
    if(not found): 
        logg("ERROR", f'Attempted sale for {input["symbol"]}, but the account is currently not holding any ')
        return
    if(amt > len(found["data"])): 
            return Status.UNSUCCESSFUL
    for i in range(amt):
        found["data"][i]["held"] = False
        found["data"][i]["date_sold"] = input["timestamp"]

        equity += input["price"]
    logg("OK", f'sold {amt} shares of {input["symbol"]}')

    return Status.OK