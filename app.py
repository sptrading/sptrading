from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from routes.scanner import router as scanner_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(scanner_router)


@app.get("/")
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
