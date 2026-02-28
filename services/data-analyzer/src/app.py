import uvicorn

from fastapi import FastAPI
from typing import List
from utils.db import pull_data, Prices, insert_analysis
from utils.fixtures import Action, MAState

app = FastAPI()


def get_buy_and_sell_signals(data: List[Prices]):
    """
    Note: the select statement already orders by date so we assume
        that the data is ordered here

    Algorithm:
        - Calculate 7-day and 30-day moving averages
        - When 7-day MA crosses from below to above 30-day, buy signal
        - When 7-day MA crosses from above to below 30-day, sell signal

    Return:
        - buy and sell signals
        - realized and unrealized gains
    """
    assert len(data) > 30, "Must provide at least 30 days of data to yield a signal"

    # calculate initial 7 and 30 day moving averages
    ma_7d = 0
    ma_30d = 0

    # end at index 28 so that we can get an initial signal at 29
    for i, d in enumerate(data[:29]):
        if i > 22:
            ma_7d += d.price / 7
        ma_30d += d.price / 30

    ma_states = []
    actions = []
    realized_gain = 0
    unrealized_gain = 0

    last_bought_price = 0

    for i, d in enumerate(data[29:]):
        # update moving averages
        ma_7d = ma_7d + (d.price / 7) - (data[i - 7].price / 7)
        ma_30d = ma_30d + (d.price / 30) - (data[i - 30].price / 30)

        # check for surplus/deficit
        if ma_7d > ma_30d:
            ma_states.append(MAState.SURPLUS)
        elif ma_7d < ma_30d:
            ma_states.append(MAState.DEFICIT)
        else:
            ma_states.append(MAState.NONE)

        if len(ma_states) == 1:
            if ma_states[i] == MAState.SURPLUS:
                actions.append(Action.BUY)
                last_bought_price = d.price
            else:
                actions.append(Action.HOLD)

        elif (ma_states[i] != ma_states[i - 1]) and (ma_states[i] == MAState.SURPLUS):
            actions.append(Action.BUY)
            last_bought_price = d.price
        elif (ma_states[i] != ma_states[i - 1]) and (ma_states[i] == MAState.DEFICIT):
            actions.append(Action.SELL)
            realized_gain = d.price - last_bought_price
            unrealized_gain = 0
        else:
            actions.append(Action.HOLD)
            unrealized_gain = d.price - last_bought_price

    return {
        "actions": actions,
        "realized_gain": realized_gain,
        "unrealized_gain": unrealized_gain,
        "date": [d.date for d in data],
        "price": [d.price for d in data],
        "data": [
            {
                "signal": actions[i],
                "date": data[i+29].date,
                "price": data[i+29].price
            }
            for i in range(len(actions))
        ]
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/analyze")
async def analyze():
    data = pull_data()
    analysis = get_buy_and_sell_signals(data)
    insert_analysis(analysis)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=80)