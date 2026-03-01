from datetime import datetime
import uvicorn

from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI, Query
from models.collect_data import CollectData
import requests
from typing import Annotated
from utils.db import insert_prices, truncate_prices

app = FastAPI()

# prometheus integration
Instrumentator().instrument(app).expose(app)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/data")
async def collect_data(params: Annotated[CollectData, Query()]):
    base_url = "https://data-api.coindesk.com/spot/v1/historical/days"
    res = requests.get(
        base_url,
        params={
            "market": "kraken",
            "instrument": "BTC-USD",
            "to_ts": int(params.end_date.timestamp()),
            "limit": (params.end_date - params.start_date).days + 1,
        },
    )

    data = res.json().get("Data")
    data = [
        {
            "date": datetime.fromtimestamp(item["TIMESTAMP"]).strftime("%Y-%m-%d"),
            "price": item["CLOSE"],
        }
        for item in data
    ]
    truncate_prices()
    insert_prices(data)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
