from fastapi import APIRouter, Request, Header, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import logging
import os
import time

from helpers.config import get_settings
from stores.embedding.EmbeddingEnum import EmbeddingEnum
from stores.embedding.EmbeddingProviderFactory import EmbeddingProviderFactory
from controllers.ChunkController import ChunkController
from controllers.EmbeddingController import EmbeddingController
from models.enums.ResponseEnum import ResponseSignal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI router
embed_router = APIRouter(
    prefix="/api/v1/embed",
    tags=["api_v1", "embed"],
)

# Pydantic model for request body validation
class EmbeddingRequest(BaseModel):
    file_name: str = Field(..., description="The name of the file to be embedded")
    provider: EmbeddingEnum = Field(..., description="Embedding provider")
    model_id: str = Field(..., description="Model identifier")
    max_input_token: int = Field(..., gt=0, description="Maximum number of input tokens")

# Dependency injection functions
def get_chunk_controller() -> ChunkController:
    return ChunkController()

def get_embedding_controller() -> EmbeddingController:
    return EmbeddingController()

def get_settings_config():
    return get_settings()

@embed_router.post("/")
async def embed_chunks(
    request: Request,
    embedding_request: EmbeddingRequest,
    api_key: Optional[str] = Header(None, alias="api-key"),
    chunk_controller: ChunkController = Depends(get_chunk_controller),
    embedding_controller: EmbeddingController = Depends(get_embedding_controller),
    settings = Depends(get_settings_config)
):
    """
    Processes and embeds text chunks using the specified embedding provider.
    
    Parameters:
    - file_name (str): Name of the file.
    - provider (EmbeddingEnum): Embedding provider.
    - model_id (str): Model ID.
    - max_input_token (int): Maximum allowed tokens for embedding.
    - api_key (Optional[str]): API key for authentication (sent in headers).

    Returns:
    - JSONResponse with execution time and success message.
    """

    logger.info(f"Received embedding request for file: {embedding_request.file_name}")

    try:
        embedding_provider_factory = EmbeddingProviderFactory(
            api_key=api_key,
            model_id=embedding_request.model_id,
            max_input_token=embedding_request.max_input_token,
        )
        embedding_client = embedding_provider_factory.create(provider=embedding_request.provider)

        # Start time measurement
        start_time = time.perf_counter()

        # Load chunks
        chunk_file_name = os.path.splitext(embedding_request.file_name)[0] + "_chunks.json"
        logger.info(f"Loading chunks from file: {chunk_file_name}")

        chunks = await chunk_controller.load_chunks(file_directory=settings.CHUNKS_DIR, file_name=chunk_file_name)

        if not chunks:
            logger.warning(f"No chunks found in {chunk_file_name}")
            raise HTTPException(status_code=400, detail="No chunks available for embedding.")

        # Generate embeddings
        logger.info(f"Generating embeddings using provider: {embedding_request.provider}")
        vectors = embedding_client.generate_embedding(chunks)

        # Save in vector database
        collection_name = os.path.splitext(embedding_request.file_name)[0]

        logger.info(f"Saving embeddings to vector database (collection: {collection_name})")
        request.app.vectordb.delete_collection(collection_name)
        request.app.vectordb.create_collection(collection_name)
        request.app.vectordb.add_vectors(collection_name=collection_name, documents=chunks, embeddings=vectors)

        # Calculate execution time
        execution_time = time.perf_counter() - start_time
        logger.info(f"Embedding process completed in {execution_time:.2f} seconds.")

        return JSONResponse(
            content={
                "message": ResponseSignal.CHUNKS_EMBEDDED_SUCCESSFULLY.value,
                "execution_time_seconds": execution_time,
            }
        )

    except FileNotFoundError:
        logger.error(f"File not found: {embedding_request.file_name}")
        raise HTTPException(status_code=404, detail="File not found.")
    
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error. Please try again later.")
