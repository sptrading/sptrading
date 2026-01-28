import requests
from config import UPSTOX_ACCESS_TOKEN
from services.instrument_map import INSTRUMENT_MAP

HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {UPSTOX_ACCESS_TOKEN}"
}

def get_all_quotes():
    keys = list(INSTRUMENT_MAP.values())
    joined = ",".join(keys)

    url = f"https://api.upstox.com/v3/market-quote/quotes?instrument_key={joined}"

    res = requests.get(url, headers=HEADERS)
    data = res.json()

    quotes = {}

    if "data" in data:
        for item in data["data"].values():
            quotes[item["instrument_token"]] = {
                "ltp": item["last_price"],
                "volume": item["volume"],
                "oi": item.get("oi", 0)
            }

    return quotes
