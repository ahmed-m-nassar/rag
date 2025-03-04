from fastapi import FastAPI
import os
from routes import base , upload , chunk
from helpers.config import get_settings
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

def initialize_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"✅ Directory created: {directory_path}")
    else:
        print(f"🔹 Directory already exists: {directory_path}")

async def startup_span():
    settings = get_settings()

    try:
        app.mongodb_connection = AsyncIOMotorClient(settings.MONGODB_CONNECTION)
        app.db_connection = app.mongodb_connection[settings.MONGODB_DATABASE_NAME]  # Connect to the "admin" database
        app.test_db_connection = app.mongodb_connection[settings.MONGODB_TEST_DATABASE_NAME]  # Connect to the "admin" database
        initialize_directory(settings.UPLOAD_DIR)
        initialize_directory(settings.CHUNKS_DIR)
        
    except Exception as e:
        print("❌ Connection failed :", e)

    print(settings.APP_NAME + " Has started")


async def shutdown_span():
    settings = get_settings()
    app.mongodb_connection.close()
    print(settings.APP_NAME + " Has Stopped")

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(base.base_router)
app.include_router(upload.upload_router)
app.include_router(chunk.chunk_router)
