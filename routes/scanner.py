from fastapi import APIRouter
from services.market_data import get_all_stocks

router = APIRouter()

@router.get("/scanner")
def scanner():
    return get_all_stocks()
