from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from routes.scanner import router as scanner_router

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.include_router(scanner_router)


@app.get("/")
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
