from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from routes.scanner import router as scanner_router

from services.data_collector import collect_data
import threading
import time

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.include_router(scanner_router)


def background_collector():
    while True:
        collect_data()
        time.sleep(60)


@app.on_event("startup")
def start_collector():
    thread = threading.Thread(target=background_collector, daemon=True)
    thread.start()


@app.get("/")
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
import json

@app.get("/debug")
def debug_data():
    try:
        with open("/tmp/live_quotes.json") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}
