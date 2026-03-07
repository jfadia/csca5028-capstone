import pytest
import app
from utils.fixtures import Action, MAState
from dataclasses import dataclass
from datetime import date, datetime
from dateutil.rrule import rrule, DAILY


@dataclass
class MockPrices:
    id: int
    date: str
    price: float


@pytest.mark.parametrize(
    "prev_state, is_initial_state",
    [
        (MAState.BREAKEVEN, False),
        (MAState.DEFICIT, False),
        (None, True),
    ],
)
def test___get_signal__buy(prev_state, is_initial_state):
    ma_7d = 10.0
    ma_30d = 5.0

    signal = app._get_signal(
        ma_7d=ma_7d,
        ma_30d=ma_30d,
        prev_state=prev_state,
        is_initial_state=is_initial_state,
    )
    assert signal == Action.BUY


@pytest.mark.parametrize(
    "prev_state, is_initial_state",
    [(MAState.SURPLUS, False), (MAState.BREAKEVEN, False)],
)
def test___get_signal__sell(prev_state, is_initial_state):
    ma_7d = 5.0
    ma_30d = 10.0

    signal = app._get_signal(
        ma_7d=ma_7d,
        ma_30d=ma_30d,
        prev_state=prev_state,
        is_initial_state=is_initial_state,
    )
    assert signal == Action.SELL


@pytest.mark.parametrize(
    "ma_7d, ma_30d, prev_state, is_initial_state",
    [
        (10.0, 10.0, MAState.SURPLUS, False),
        (15.0, 10.0, MAState.SURPLUS, False),
        (10.0, 10.0, MAState.DEFICIT, False),
        (5.0, 10.0, MAState.DEFICIT, False),
        (10.0, 10.0, None, True),
    ],
)
def test___get_signal__hold(ma_7d, ma_30d, prev_state, is_initial_state):
    signal = app._get_signal(
        ma_7d=ma_7d,
        ma_30d=ma_30d,
        prev_state=prev_state,
        is_initial_state=is_initial_state,
    )
    assert signal == Action.HOLD


def test___get_cur_state__surplus():
    ma_7d = 10.0
    ma_30d = 5.0

    state = app._get_cur_state(ma_7d=ma_7d, ma_30d=ma_30d)
    assert MAState.SURPLUS == state


def test___get_cur_state__deficit():
    ma_7d = 5.0
    ma_30d = 10.0

    state = app._get_cur_state(ma_7d=ma_7d, ma_30d=ma_30d)
    assert MAState.DEFICIT == state


def test___get_cur_state__breakeven():
    ma_7d = 10.0
    ma_30d = 10.0

    state = app._get_cur_state(ma_7d=ma_7d, ma_30d=ma_30d)
    assert MAState.BREAKEVEN == state


def test__get_buy_and_sell_signals__monotonic_increasing():
    data = []
    for i, d in enumerate(rrule(DAILY, dtstart=date(2026, 1, 1), until=date(2026, 2, 14))):
        data.append(MockPrices(id=i, date=d, price=i))
    
    res = app.get_buy_and_sell_signals(data)

    assert len(res["data"]) == 15
    assert res["data"][-1]["date"] == datetime(2026, 2, 14, 0, 0)
    assert res["data"][0]["signal"] == Action.BUY
    assert res["data"][-1]["signal"] == Action.HOLD
    assert len(set(i["signal"] for i in res["data"][1:])) == 1
    assert res["realized_gain"] == 0
    assert res["unrealized_gain"] == 14


def test__get_buy_and_sell_signals__monotonic_decreasing():
    data = []
    for i, d in enumerate(rrule(DAILY, dtstart=date(2026, 1, 1), until=date(2026, 2, 14))):
        data.append(MockPrices(id=i, date=d, price=45-i))
    
    res = app.get_buy_and_sell_signals(data)

    assert len(res["data"]) == 15
    assert res["data"][-1]["date"] == datetime(2026, 2, 14, 0, 0)
    assert res["data"][0]["signal"] == Action.HOLD
    assert len(set(i["signal"] for i in res["data"][1:])) == 1
    assert res["realized_gain"] == 0
    assert res["unrealized_gain"] == 0