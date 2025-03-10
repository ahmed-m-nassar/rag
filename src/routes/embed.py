from fastapi import APIRouter,Request ,Header , Body
from fastapi.responses import JSONResponse
from typing import Optional
import logging
import os
from helpers.config import get_settings
from stores.embedding.EmbeddingEnum import EmbeddingEnum
from stores.embedding.EmbeddingProviderFactory import EmbeddingProviderFactory
from controllers.ChunkController import ChunkController
from controllers.EmbeddingController import EmbeddingController
from models.enums.ResponseEnum import ResponseSignal

import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

embed_router = APIRouter(
    prefix="/api/v1/embed",
    tags=["api_v1", "embed"],
)

@embed_router.post("/")
async def embed_chunks(request : Request ,
                       file_name : str = Body(...) , 
                       provider : EmbeddingEnum = Body(...) ,
                       model_id : str = Body(...),
                       max_input_token : int = Body(...),
                       api_key : Optional[str] = Header(None, alias="api-key") 
                        ):
    
    settings = get_settings()
    chunk_controller = ChunkController()
    embedding_controller = EmbeddingController()

    embedding_provider_factory = EmbeddingProviderFactory(
                                                          api_key=api_key,
                                                          model_id=model_id,
                                                          max_input_token=max_input_token
                                                         )
    
    embedding_client = embedding_provider_factory.create(provider=provider) 

    # Start time measurement
    start_time = time.perf_counter()

    # load chunks
    chunk_file_name= os.path.splitext(file_name)[0] + "_chunks.json"
    print(file_name)
    print(chunk_file_name)
    chunks = await chunk_controller.load_chunks(file_directory=settings.CHUNKS_DIR , file_name=chunk_file_name)
    print(chunks)
    # generate embeddings
    vectors = embedding_client.generate_embedding(chunks)

    # Save in vector database
    collection_name =os.path.splitext(file_name)[0]
    request.app.vectordb.delete_collection(collection_name)
    request.app.vectordb.create_collection(collection_name)
    request.app.vectordb.add_vectors(collection_name = collection_name , documents = chunks, embeddings = vectors)

    #await embedding_controller.save_embeddings(file_directory = settings.EMBEDDINGS_DIR , file_name='embeddings.json', embeddings = vectors)
    #Calculate time
    end_time = time.perf_counter()
    execution_time = end_time - start_time


    return JSONResponse(
        content={
            "message": ResponseSignal.CHUNKS_EMBEDDED_SUCCESSFULLY.value,
            "execution_time_seconds": execution_time  # Include execution time
        }
    )
