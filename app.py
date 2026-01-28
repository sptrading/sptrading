from fastapi import FastAPI
from routes.api import router as api_router
from routes.home import router as home_router

app = FastAPI()

app.include_router(home_router)
app.include_router(api_router)
