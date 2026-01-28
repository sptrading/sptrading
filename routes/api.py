from fastapi import APIRouter
from services.market_data import get_ltp

router = APIRouter(prefix="/api")

@router.get("/ltp/{symbol}")
def ltp(symbol: str):
    return get_ltp(symbol)
