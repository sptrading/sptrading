import json
import time
from datetime import datetime
from services.market_data import get_quote
from services.instrument_map import INSTRUMENT_MAP

DATA_FILE = "data/live_quotes.json"


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
