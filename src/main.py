from fastapi import FastAPI
import numpy as np
import os
from routes import base , upload , chunk , embed , visualize , retrieve , rerank , generate
from helpers.config import get_settings
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from sentence_transformers import SentenceTransformer
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from stores.reranking.RerankingEnum import RerankingModelsProvidersEnums
from stores.reranking.RerankingEnum import HuggingFaceLocalModelIdsEnum
from stores.reranking.RerankingProviderFactory import RerankerProviderFactory
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.llm.LLMEnum import LLMsProviders
import torch
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
        initialize_directory(settings.EMBEDDING_MODELS_DIR)
        initialize_directory(settings.RERANKING_MODELS_DIR)
        initialize_directory(settings.VISUALIZATIONS_DIR)
        initialize_directory(settings.VECTORDB_PATH)
        
        vectordb_provider_factory = VectorDBProviderFactory()
        app.vectordb = vectordb_provider_factory.create(provider="chromadb" , path=settings.VECTORDB_PATH)
        app.vectordb.connect()


        reranker = RerankerProviderFactory.get_reranker(
            provider=RerankingModelsProvidersEnums.HuggingFaceLocal,
            model_id=HuggingFaceLocalModelIdsEnum.MMACRO_MMINILM_V2_L12
        )

  

        # llm_client = LLMProviderFactory.get_llm(base_url="https://5624-34-125-232-45.ngrok-free.app/api/chat",
        #                            model_id="phi4:14b-q4_K_M" ,
        #                            provider=LLMsProviders.OLLAMA , 
        #                            system_prompt="You are a helpful ai assistant , answer the questions in short answers."
        #                            )
        
        # print(llm_client.generate_response(prompt="what is the capital of egypt"))

        # app.mongodb_connection = AsyncIOMotorClient(settings.MONGODB_CONNECTION)
        # app.db_connection = app.mongodb_connection[settings.MONGODB_DATABASE_NAME]  # Connect to the "admin" database
        # app.test_db_connection = app.mongodb_connection[settings.MONGODB_TEST_DATABASE_NAME]  # Connect to the "admin" database



        # Choose a model (Example: 'cross-encoder/ms-marco-MiniLM-L-6-v2')
        # MODEL_NAME = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
        # SAVE_PATH = settings.RERANKING_MODELS_DIR  # Directory to save the model

        # # Load model and tokenizer
        # tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        # model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

        # # Save model and tokenizer locally
        # model.save_pretrained(SAVE_PATH)
        # tokenizer.save_pretrained(SAVE_PATH)

        # print(f"Model saved at {SAVE_PATH}")


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
app.include_router(rerank.rerank_router)
app.include_router(generate.generate_router)
