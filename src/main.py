from fastapi import FastAPI
from routes import base
from helpers.config import get_settings


app = FastAPI()

async def startup_span():
    settings = get_settings()
    print(settings.APP_NAME + " Has started")


async def shutdown_span():
    settings = get_settings()
    print(settings.APP_NAME + " Has Stopped")

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(base.base_router)
