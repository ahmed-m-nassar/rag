from fastapi import APIRouter, Request, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import logging
import os

from controllers.NLPController import NLPController
from helpers.config import get_settings
from models.enums.SearchTechniqueEnum import SearchTechniqueEnums
from stores.embedding.EmbeddingProviderFactory import EmbeddingProviderFactory
from stores.embedding.EmbeddingEnum import EmbeddingEnum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

retrieve_router = APIRouter(
    prefix="/api/v1/retrieve",
    tags=["api_v1", "retrieve"],
)

class RetrieveRequest(BaseModel):
    file_name: str = Field(..., description="The name of the file uploaded.")
    query: str = Field(..., description="User query for semantic search.")
    search_technique: SearchTechniqueEnums = Field(..., description="Search technique to use.")
    n_results: int = Field(..., ge=1, le=100, description="Number of search results to return (1-100).")
    provider: EmbeddingEnum = Field(..., description="Embedding provider to use.")
    model_id: str = Field(..., description="Model identifier for the embedding provider.")
    max_input_token: int = Field(..., gt=0, description="Max input tokens for the embedding model.")

def get_nlp_controller() -> NLPController:
    """Dependency injection for NLPController instance."""
    return NLPController()

@retrieve_router.post("/")
async def retrieve(
    request: Request,
    retrieve_request: RetrieveRequest,  
    api_key: Optional[str] = Header(None, alias="api-key"),
    nlp_controller: NLPController = Depends(get_nlp_controller),
):
    """
    Handles retrieval requests 

    - Retrieves relevant document chunks based on the query using embeddings.
    - Uses a specified search technique to retrieve `n_results` from the vector database.

    Returns:
        JSONResponse containing search results.
    """
    
    try:
        collection_name = os.path.splitext(retrieve_request.file_name)[0]

        # Initialize embedding provider
        embedding_provider_factory = EmbeddingProviderFactory(
            api_key=api_key,
            model_id=retrieve_request.model_id,
            max_input_token=retrieve_request.max_input_token
        )

        # Create embedding client
        embedding_client = embedding_provider_factory.create(provider=retrieve_request.provider)

        if not embedding_client:
            logger.error(f"Invalid embedding provider: {retrieve_request.provider}")
            raise HTTPException(status_code=400, detail="Invalid embedding provider.")

        # Perform semantic search
        search_results = await nlp_controller.semantic_search(
            collection_name=collection_name,
            embedding_client=embedding_client,
            n_results=retrieve_request.n_results,
            query=retrieve_request.query,
            vectordb=request.app.vectordb,
        )

        logger.info(f"Search completed for file: {retrieve_request.file_name}, results found: {len(search_results)}")
        return {"results": search_results}

    except HTTPException as http_exc:
        raise http_exc  

    except Exception as e:
        logger.error(f"Unexpected error during retrieval: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
