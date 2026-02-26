import pytest
from models import collect_data


def test_collect_data_model():
    data = {"start_date": "2024-01-01", "end_date": "2024-01-31"}
    model = collect_data.CollectData(**data)
    assert model.start_date.strftime("%Y-%m-%d") == data["start_date"]
    assert model.end_date.strftime("%Y-%m-%d") == data["end_date"]


def test_collect_data_model_invalid_date():
    data = {"start_date": "2025-01", "end_date": 5}
    with pytest.raises(Exception):
        collect_data.CollectData(**data)
