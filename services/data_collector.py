import time
import json
import requests
from config import UPSTOX_ACCESS_TOKEN
from services.instrument_map import INSTRUMENT_MAP

DATA_FILE = "/tmp/live_quotes.json"

HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {UPSTOX_ACCESS_TOKEN}"
}


def fetch_quote(key):
    url = f"https://api.upstox.com/v3/market-quote/quotes?instrument_key={key}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    print("URL:", url)
    print("RESPONSE:", r.text)
    return r.json()


def collect_data():
    all_data = {}

    for symbol, key in INSTRUMENT_MAP.items():
        print("Fetching:", symbol, key)
        res = fetch_quote(key)

        if "data" not in res:
            print("ERROR FOR:", symbol, res)
            continue

        q = list(res["data"].values())[0]

        all_data[symbol] = {
            "ltp": q["last_price"],
            "vwap": q["vwap"],
            "high": q["ohlc"]["high"],
            "low": q["ohlc"]["low"],
            "open": q["ohlc"]["open"],
            "prev_close": q["ohlc"]["close"],
            "volume": q["volume"]
        }

        time.sleep(0.2)

    with open(DATA_FILE, "w") as f:
        json.dump(all_data, f)

    print("FILE WRITTEN:", len(all_data))


def start_background_collection():
    while True:
        collect_data()
        time.sleep(20)
