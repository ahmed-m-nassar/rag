from fastapi import FastAPI
import numpy as np
import os
from routes import base , upload , chunk , embed , visualize , retrieve
from helpers.config import get_settings
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from sentence_transformers import SentenceTransformer
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
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
        initialize_directory(settings.UPLOAD_DIR)
        initialize_directory(settings.CHUNKS_DIR)
        initialize_directory(settings.EMBEDDINGS_DIR)
        initialize_directory(settings.VISUALIZATIONS_DIR)
        initialize_directory(settings.VECTORDB_PATH)
        
        vectordb_provider_factory = VectorDBProviderFactory()
        app.vectordb = vectordb_provider_factory.create(provider="chromadb" , path=settings.VECTORDB_PATH)
        app.vectordb.connect()
        print(app.vectordb.get_collection_info("test"))
        # app.mongodb_connection = AsyncIOMotorClient(settings.MONGODB_CONNECTION)
        # app.db_connection = app.mongodb_connection[settings.MONGODB_DATABASE_NAME]  # Connect to the "admin" database
        # app.test_db_connection = app.mongodb_connection[settings.MONGODB_TEST_DATABASE_NAME]  # Connect to the "admin" database

        

    except Exception as e:
        print("❌ Connection failed :", e)

    print(settings.APP_NAME + " Has started")


async def shutdown_span():
    settings = get_settings()
    app.vectordb.disconnect()
    # app.mongodb_connection.close()
    print(settings.APP_NAME + " Has Stopped")

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(base.base_router)
app.include_router(upload.upload_router)
app.include_router(chunk.chunk_router)
app.include_router(embed.embed_router)
app.include_router(visualize.visualize_router)
app.include_router(retrieve.retrieve_router)
