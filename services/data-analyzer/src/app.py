import pika
import os
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI
from typing import List
from utils.db import pull_data, Prices, insert_analysis
from utils.fixtures import Action, MAState

app = FastAPI()

# prometheus integration
Instrumentator().instrument(app).expose(app)

RABBITMQ_HOST = os.environ["RABBITMQ_HOST"]
RABBITMQ_QUEUE = os.environ["RABBITMQ_QUEUE"]


def _update_moving_average(arr: List[Prices]):
    return sum(i.price for i in arr) / len(arr)


def _get_cur_state(*, ma_7d: float, ma_30d: float):
    if ma_7d > ma_30d:
        return MAState.SURPLUS
    elif ma_7d < ma_30d:
        return MAState.DEFICIT
    elif ma_7d == ma_30d:
        return MAState.BREAKEVEN


def _get_signal(
    *,
    ma_7d: float,
    ma_30d: float,
    prev_state: MAState = None,
    is_initial_state: bool = False
):
    cur_state = _get_cur_state(ma_7d=ma_7d, ma_30d=ma_30d)
    if not is_initial_state:
        if cur_state == prev_state:
            return Action.HOLD

    if ma_7d > ma_30d:
        return Action.BUY
    elif (ma_7d < ma_30d) and (not is_initial_state):
        return Action.SELL
    else:
        return Action.HOLD


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
    realized_gain = 0
    unrealized_gain = 0
    last_bought_at = None

    res = []

    for i in range(30, len(data)):
        ma_7d = _update_moving_average(data[i - 7 : i])
        ma_30d = _update_moving_average(data[i - 30 : i])

        if len(res) == 0:
            signal = _get_signal(ma_7d=ma_7d, ma_30d=ma_30d, is_initial_state=True)
        else:
            signal = _get_signal(ma_7d=ma_7d, ma_30d=ma_30d, prev_state=cur_state)

        if signal == Action.BUY:
            last_bought_at = data[i].price
        elif signal == Action.SELL:
            unrealized_gain = 0
            realized_gain = data[i].price - last_bought_at
        elif (signal == Action.HOLD) and (last_bought_at is not None):
            unrealized_gain = data[i].price - last_bought_at

        res.append(
            {
                "signal": signal,
                "date": data[i].date,
                "price": data[i].price,
            }
        )

        cur_state = _get_cur_state(ma_7d=ma_7d, ma_30d=ma_30d)

    return {
        "realized_gain": realized_gain,
        "unrealized_gain": unrealized_gain,
        "data": res,
    }


def analyze(*args, **kwargs):
    data = pull_data()
    analysis = get_buy_and_sell_signals(data)
    insert_analysis(analysis)


if __name__ == "__main__":
    with pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    ) as connection:
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE)
        channel.basic_consume(
            queue=RABBITMQ_QUEUE, auto_ack=True, on_message_callback=analyze
        )
        channel.start_consuming()
