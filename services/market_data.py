import requests
from config import UPSTOX_ACCESS_TOKEN
from services.instrument_map import INSTRUMENT_MAP

HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {UPSTOX_ACCESS_TOKEN}"
}


def get_ltp(symbol: str):
    key = INSTRUMENT_MAP.get(symbol.upper())

    if not key:
        return {"error": "Invalid symbol"}

    url = f"https://api.upstox.com/v3/market-quote/ltp?instrument_key={key}"
    res = requests.get(url, headers=HEADERS)
    return res.json()

def get_multiple_ltp(symbols: list):
    results = []

    for sym in symbols:
        data = get_ltp(sym)
        try:
            price = list(data["data"].values())[0]["last_price"]
            results.append({"symbol": sym, "price": price})
        except:
            results.append({"symbol": sym, "price": "Error"})

    return results
