from fastapi import APIRouter
from services.market_data import run_scanner

router = APIRouter()

@router.get("/scanner")
def scanner():
    breakout, boost = run_scanner()
    return {
        "breakout": breakout,
        "intraday_boost": boost
    }
