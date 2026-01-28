from fastapi import APIRouter
from services.data_collector import collect_data
from services.market_data import run_scanner

router = APIRouter()


@router.get("/scanner")
def scanner():
    # First collect fresh data
    collect_data()

    # Then run maths on stored data
    breakout, boost = run_scanner()

    return {
        "breakout": breakout[:10],
        "intraday_boost": boost[:10],
    }
