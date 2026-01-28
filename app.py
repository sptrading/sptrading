from fastapi import FastAPI
from routes.scanner import router as scanner_router
from threading import Thread
from services.data_collector import start_background_collection

app = FastAPI()

app.include_router(scanner_router)

@app.on_event("startup")
def startup_event():
    t = Thread(target=start_background_collection, daemon=True)
    t.start()


@app.get("/")
def root():
    return {"status": "running"}
