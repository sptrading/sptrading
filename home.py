from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.market_data import get_multiple_ltp
from services.instrument_map import INSTRUMENT_MAP

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):

    all_symbols = list(INSTRUMENT_MAP.keys())

    breakout_symbols = all_symbols[:10]
    intraday_symbols = all_symbols[10:20]

    breakout = get_multiple_ltp(breakout_symbols)
    intraday = get_multiple_ltp(intraday_symbols)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "breakout": breakout,
        "intraday": intraday
    })
