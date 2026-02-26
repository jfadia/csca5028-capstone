from utils import db


def test_integration__insert_prices():
    data = [
        {"date": "2024-01-01", "price": 100},
        {"date": "2024-01-02", "price": 110},
    ]
    db.insert_prices(data)


def test_integration__truncate_prices():
    db.truncate_prices()
