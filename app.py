from fastapi import FastAPI
from threading import Thread
from services.data_collector import start_background_collection
from services.market_data import get_all_stocks

app = FastAPI()


@app.on_event("startup")
def startup_event():
    t = Thread(target=start_background_collection, daemon=True)
    t.start()


@app.get("/scanner")
def scanner():
    return get_all_stocks()


@app.get("/")
def root():
    return {"status": "running"}
