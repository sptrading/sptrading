import json

DATA_FILE = "/tmp/live_quotes.json"


def load_live_data():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
        return {}


def get_all_stocks():
    data = load_live_data()
    stocks = []

    for symbol, s in data.items():
        stocks.append({
            "symbol": symbol,
            "ltp": s.get("ltp"),
            "vwap": s.get("vwap"),
            "high": s.get("high"),
            "low": s.get("low"),
            "open": s.get("open"),
            "prev_close": s.get("prev_close"),
            "volume": s.get("volume"),
        })

    return stocks
