trail = []
counterfeit_money = 1000000000
bagholder_log = [
    # {
    #   symbol: string
    #   data: [
    #   {
    #       date
    #       price
    #       amount
    #   }
    # ]

    # }
    {
        "symbol": "BTC/USD",
        "data": []
    }
]
data = [
        {
            "limit": 2,
            "avg": 0,
            "low": 0,
            "high": 0
        },
        {
            "limit": 4,
            "avg": 0,
            "low": 0,
            "high": 0
        },
        {
            "limit": 6,
            "avg": 0,
            "low": 0,
            "high": 0
        },
    ]

def get_fake():
    return data

def fake(input):
    trail.append(input["price"])
    print(trail[-1])
    # update all time range values
    for entry in data:
        if(len(trail) < entry["limit"]):
            entry["low"] = min(trail)
            entry["high"] = max(trail)
            entry["avg"] = sum(trail)/len(trail)
            continue
        
        # updates values for each time range
        entry["avg"] = sum(trail[(entry["limit"]-1):])/len(trail[(entry["limit"]-1):])
        entry["low"] = min(
            trail[(entry["limit"]-1):]
            )
        entry["high"] = max(
            trail[(entry["limit"]-1):]
            )
        
    for entry in data:
        # market actions
        if(round(input["price"]) == round(entry["low"])):
            trigger_buy()

# alpaca portfolio/rebalance actions

def trigger_buy(ticker, amt=1):
    # todo
    return

def trigger_sell(ticker, amt=1):
    # todo
    return