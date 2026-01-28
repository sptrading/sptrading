import json
from services.instrument_map import INSTRUMENT_MAP


# -------- SAFE LOAD STORED DATA -------- #

def load_live_data():
    try:
        with open("data/live_quotes.json") as f:
            return json.load(f)
    except:
        return {}


# -------- MATHS -------- #

def calculate_pc_sp(ltp, prev_close, open_p):
    pc = ((ltp - prev_close) / prev_close) * 100
    sp = ((ltp - open_p) / open_p) * 100
    return pc, sp


def rfac(ltp, open_p, dh, dl, vspike, vwap):
    day_range = dh - dl if dh - dl != 0 else 1
    vwap_factor = abs(ltp - vwap) / day_range
    return ((ltp - open_p) / day_range) * vspike * vwap_factor


# -------- CONDITIONS -------- #

def is_breakout(pc, sp, vspike):
    return pc > 1.2 and sp > 0.8 and vspike > 1.5


def is_intraday_boost(rf, pc):
    return rf > 1.2 and abs(pc) > 1


# -------- SCANNER -------- #

def scan_stock(symbol: str, live):
    data = live[symbol]

    ltp = data["ltp"]
    open_p = data["open"]
    dh = data["high"]
    dl = data["low"]
    prev_close = data["prev_close"]
    volume = data["volume"]

    pc, sp = calculate_pc_sp(ltp, prev_close, open_p)

    vspike = abs(pc) + abs(sp)
    vwap = (dh + dl) / 2

    rf = rfac(ltp, open_p, dh, dl, vspike, vwap)

    side = "BUY" if ltp > open_p else "SELL"

    return {
        "symbol": symbol,
        "%": round(pc, 2),
        "signal%": round(sp, 2),
        "side": side,
        "breakout": is_breakout(pc, sp, vspike),
        "intraday_boost": is_intraday_boost(rf, pc),
        "rfac": round(rf, 2),
    }


def run_scanner():
    live = load_live_data()

    if not live:
        return [], []

    breakout = []
    boost = []

    for sym in INSTRUMENT_MAP.keys():
        if sym not in live:
            continue

        data = scan_stock(sym, live)

        if data["breakout"]:
            breakout.append(data)

        if data["intraday_boost"]:
            boost.append(data)

    breakout = sorted(breakout, key=lambda x: x["signal%"], reverse=True)
    boost = sorted(boost, key=lambda x: x["rfac"], reverse=True)

    return breakout, boost
