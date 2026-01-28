from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from routes.scanner import router as scanner_router

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.include_router(scanner_router)


@app.get("/")
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
from services.data_collector import collect_data
import threading
import time


def background_collector():
    while True:
        collect_data()
        time.sleep(60)  # प्रत्येक 1 मिनिटाला data store


@app.on_event("startup")
def start_collector():
    thread = threading.Thread(target=background_collector, daemon=True)
    thread.start()
