import requests
from datetime import datetime, timedelta

from config import UPSTOX_ACCESS_TOKEN
from services.instrument_map import INSTRUMENT_MAP


BASE_URL = "https://api.upstox.com/v3"
HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {UPSTOX_ACCESS_TOKEN}"
}


# ---------------- QUOTE DATA ---------------- #

def get_quote(instrument_key: str):
    url = f"{BASE_URL}/market-quote/quotes?instrument_key={instrument_key}"
    res = requests.get(url, headers=HEADERS).json()
    return list(res["data"].values())[0]


# ---------------- INTRADAY CANDLES (5 MIN) ---------------- #

def get_intraday_candles(instrument_key: str):
    url = f"{BASE_URL}/historical-candle/intraday/{instrument_key}/minutes/5"
    res = requests.get(url, headers=HEADERS).json()
    return res["data"]["candles"]


# ---------------- HISTORICAL (DAY) ---------------- #

def get_historical_days(instrument_key: str, days=10):
    to_date = datetime.now().date()
    from_date = to_date - timedelta(days=days+5)

    url = (
        f"{BASE_URL}/historical-candle/{instrument_key}/day/1/"
        f"{to_date}/{from_date}"
    )
    res = requests.get(url, headers=HEADERS).json()
    return res["data"]["candles"]


# ---------------- MATHS FUNCTIONS ---------------- #

def quote_maths(q):
    ltp = q["last_price"]
    prev_close = q["prev_close"]
    open_price = q["open"]
    volume = q["volume"]
    day_high = q["high"]
    day_low = q["low"]

    percent_change = ((ltp - prev_close) / prev_close) * 100
    signal_percent = ((ltp - open_price) / open_price) * 100

    return ltp, percent_change, signal_percent, volume, day_high, day_low, open_price


def get_orb_high(candles):
    first_three = candles[:3]
    highs = [c[2] for c in first_three]
    return max(highs)


def volume_spike(current_volume, historical_candles):
    vols = [c[5] for c in historical_candles[-10:]]
    avg_vol = sum(vols) / len(vols)
    return current_volume / avg_vol, avg_vol


def candle_imbalance(candle):
    o, h, l, c = candle[1], candle[2], candle[3], candle[4]
    body = abs(c - o)
    rng = h - l if h - l != 0 else 1
    imbalance = body / rng
    side = "BUY" if c > o else "SELL"
    return imbalance, side


def big_candle(current, candles):
    sizes = [(c[2] - c[3]) for c in candles[-10:]]
    avg_size = sum(sizes) / len(sizes)
    curr_size = current[2] - current[3]
    return curr_size > (2 * avg_size)


def volatility_factor(day_high, day_low, hist):
    ranges = [(c[2] - c[3]) for c in hist[-10:]]
    avg_range = sum(ranges) / len(ranges)
    today_range = day_high - day_low
    return today_range / avg_range


def rfac(ltp, open_p, day_high, day_low, vol_spike, vol_factor):
    day_range = day_high - day_low if day_high - day_low != 0 else 1
    return ((ltp - open_p) / day_range) * vol_spike * vol_factor


# ---------------- CONDITIONS ---------------- #

def is_breakout(pc, sp, ltp, orb, vspike):
    return pc > 3 and sp > 2 and ltp > orb and vspike > 2


def is_intraday_boost(rf, pc, imb, big, vspike):
    return rf > 3 and abs(pc) > 2 and imb > 0.6 and big and vspike > 3


# ---------------- MAIN SCANNER ---------------- #

def scan_stock(symbol: str):
    key = INSTRUMENT_MAP[symbol]

    quote = get_quote(key)
    candles = get_intraday_candles(key)
    hist = get_historical_days(key)

    ltp, pc, sp, vol, dh, dl, op = quote_maths(quote)

    orb = get_orb_high(candles)
    vspike, _ = volume_spike(vol, hist)

    last_candle = candles[-1]
    imb, side = candle_imbalance(last_candle)
    big = big_candle(last_candle, candles)
    vfac = volatility_factor(dh, dl, hist)
    rf = rfac(ltp, op, dh, dl, vspike, vfac)

    result = {
        "symbol": symbol,
        "ltp": round(ltp, 2),
        "%": round(pc, 2),
        "signal%": round(sp, 2),
        "side": side,
        "breakout": is_breakout(pc, sp, ltp, orb, vspike),
        "intraday_boost": is_intraday_boost(rf, pc, imb, big, vspike),
        "rfac": round(rf, 2)
    }

    return result


def run_scanner():
    breakout_list = []
    boost_list = []

    for sym in INSTRUMENT_MAP.keys():
        try:
            data = scan_stock(sym)

            if data["breakout"]:
                breakout_list.append(data)

            if data["intraday_boost"]:
                boost_list.append(data)

        except Exception:
            continue

    breakout_list = sorted(breakout_list, key=lambda x: x["signal%"], reverse=True)
    boost_list = sorted(boost_list, key=lambda x: x["rfac"], reverse=True)

    return breakout_list, boost_list
