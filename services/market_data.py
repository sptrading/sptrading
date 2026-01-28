import requests
from datetime import datetime, timedelta

from config import UPSTOX_ACCESS_TOKEN
from services.instrument_map import INSTRUMENT_MAP

BASE_URL = "https://api.upstox.com/v3"
HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {UPSTOX_ACCESS_TOKEN}"
}


# ---------------- API ---------------- #

def get_quote(token: str):
    url = f"{BASE_URL}/market-quote/quotes?instrument_key={token}"
    res = requests.get(url, headers=HEADERS).json()
    return list(res["data"].values())[0]


def get_intraday_candles(token: str):
    url = f"{BASE_URL}/historical-candle/intraday/{token}/minutes/5"
    res = requests.get(url, headers=HEADERS).json()
    return res["data"]["candles"]


def get_historical_days(token: str, days=12):
    to_date = datetime.now().date()
    from_date = to_date - timedelta(days=days)

    url = f"{BASE_URL}/historical-candle/{token}/day/1/{to_date}/{from_date}"
    res = requests.get(url, headers=HEADERS).json()
    return res["data"]["candles"]


# ---------------- MATHS ---------------- #

def calculate_vwap(candles):
    total_pv = 0
    total_vol = 0

    for c in candles:
        h, l, close, vol = c[2], c[3], c[4], c[5]
        tp = (h + l + close) / 3
        total_pv += tp * vol
        total_vol += vol

    return total_pv / total_vol if total_vol else 0


def get_orb_high(candles):
    highs = [c[2] for c in candles[:3]]
    return max(highs)


def volume_spike(current_volume, hist):
    vols = [c[5] for c in hist[-10:]]
    avg_vol = sum(vols) / len(vols)
    return current_volume / avg_vol


def candle_imbalance(candle):
    o, h, l, c = candle[1], candle[2], candle[3], candle[4]
    body = abs(c - o)
    rng = h - l if h - l != 0 else 1
    imb = body / rng
    side = "BUY" if c > o else "SELL"
    return imb, side


def rfac(ltp, open_p, dh, dl, vspike, vwap):
    day_range = dh - dl if dh - dl != 0 else 1
    vwap_factor = abs(ltp - vwap) / day_range
    return ((ltp - open_p) / day_range) * vspike * vwap_factor


# ---------------- CONDITIONS (LIVE TUNED) ---------------- #

def is_breakout(pc, sp, ltp, orb, vspike):
    return pc > 1.2 and sp > 0.8 and ltp > orb and vspike > 1.5


def is_intraday_boost(rf, pc, imb, vspike, ltp, vwap):
    return (
        rf > 1.2 and
        abs(pc) > 1 and
        imb > 0.45 and
        vspike > 1.8 and
        ((ltp > vwap) or (ltp < vwap))
    )


# ---------------- MAIN SCAN ---------------- #

def scan_stock(symbol: str):
    token = INSTRUMENT_MAP[symbol]

    quote = get_quote(token)
    candles = get_intraday_candles(token)
    hist = get_historical_days(token)

    ltp = quote["last_price"]
    prev_close = quote["prev_close"]
    open_p = quote["open"]
    volume = quote["volume"]
    dh = quote["high"]
    dl = quote["low"]

    pc = ((ltp - prev_close) / prev_close) * 100
    sp = ((ltp - open_p) / open_p) * 100

    orb = get_orb_high(candles)
    vspike = volume_spike(volume, hist)

    imb, side = candle_imbalance(candles[-1])
    vwap = calculate_vwap(candles)
    rf = rfac(ltp, open_p, dh, dl, vspike, vwap)

    return {
        "symbol": symbol,
        "%": round(pc, 2),
        "signal%": round(sp, 2),
        "side": side,
        "breakout": is_breakout(pc, sp, ltp, orb, vspike),
        "intraday_boost": is_intraday_boost(rf, pc, imb, vspike, ltp, vwap),
        "rfac": round(rf, 2),
    }


def run_scanner():
    breakout = []
    boost = []

    for sym in INSTRUMENT_MAP.keys():
        try:
            data = scan_stock(sym)

            if data["breakout"]:
                breakout.append(data)

            if data["intraday_boost"]:
                boost.append(data)

        except Exception:
            continue

    breakout = sorted(breakout, key=lambda x: x["signal%"], reverse=True)
    boost = sorted(boost, key=lambda x: x["rfac"], reverse=True)

    return breakout, boost
