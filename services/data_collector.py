import json
import requests
from datetime import datetime
from config import UPSTOX_ACCESS_TOKEN
from services.instrument_map import INSTRUMENT_MAP

DATA_FILE = "/tmp/live_quotes.json"


HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {UPSTOX_ACCESS_TOKEN}"
}

BASE_URL = "https://api.upstox.com/v3"


def get_quote(token: str):
    url = f"{BASE_URL}/market-quote/quotes?instrument_key={token}"
    res = requests.get(url, headers=HEADERS).json()
    return list(res["data"].values())[0]


def collect_data():
    all_data = {}

    for sym, token in INSTRUMENT_MAP.items():
        try:
            q = get_quote(token)
            all_data[sym] = {
                "ltp": q["last_price"],
                "open": q["open"],
                "high": q["high"],
                "low": q["low"],
                "prev_close": q["prev_close"],
                "volume": q["volume"],
                "time": str(datetime.now())
            }
        except:
            continue

    with open(DATA_FILE, "w") as f:
        json.dump(all_data, f, indent=2)
