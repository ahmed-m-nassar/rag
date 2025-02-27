from fastapi import FastAPI
from routes import base , file
from helpers.config import get_settings
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

async def startup_span():
    settings = get_settings()

    try:
        app.mongodb_connection = AsyncIOMotorClient(settings.MONGODB_CONNECTION)
        app.db_connection = app.mongodb_connection[settings.MONGODB_DATABASE_NAME]  # Connect to the "admin" database
        app.test_db_connection = app.mongodb_connection[settings.MONGODB_TEST_DATABASE_NAME]  # Connect to the "admin" database
    
    except Exception as e:
        print("❌ Connection failed:", e)

    print(settings.APP_NAME + " Has started")


async def shutdown_span():
    settings = get_settings()
    app.mongodb_connection.close()
    print(settings.APP_NAME + " Has Stopped")

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(base.base_router)
app.include_router(file.file_router)
