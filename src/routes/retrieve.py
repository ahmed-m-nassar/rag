from fastapi import APIRouter,Request
from fastapi.responses import JSONResponse
import logging
import os
from controllers.SearchController  import SearchController
from helpers.config import get_settings
from models.enums.SearchTechniqueEnum import SearchTechniqueEnums
from stores.embedding.EmbeddingProviderFactory import EmbeddingProviderFactory
from fastapi import APIRouter,Request ,Header , Body
from stores.embedding.EmbeddingEnum import EmbeddingEnum
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

retrieve_router = APIRouter(
    prefix="/api/v1/retrieve",
    tags=["api_v1", "retrieve"],
)

@retrieve_router.post("/")
async def retrieve(
    request: Request,
    file_name: str = Body(...),
    query: str = Body(...),
    search_technique: SearchTechniqueEnums = Body(...),
    n_results: int = Body(...),
    provider: EmbeddingEnum = Body(...),
    model_id: str = Body(...),
    max_input_token: int = Body(...),
    api_key: Optional[str] = Header(None, alias="api-key")
):
    settings = get_settings()
    search_controller = SearchController()
    # Initialize embedding provider
    embedding_provider_factory = EmbeddingProviderFactory(
        api_key=api_key,
        model_id=model_id,
        max_input_token=max_input_token
    )
    
    # Create embedding client
    embedding_client = embedding_provider_factory.create(provider=provider)
    
    if not embedding_client:
        return JSONResponse(status_code=400, content={"error": "Invalid embedding provider"})

    search_results = await search_controller.semantic_search(collection_name=os.path.splitext(file_name)[0],
                                      embedding_client=embedding_client ,
                                      n_results=n_results,
                                      query=query,
                                      vectordb=request.app.vectordb,
                                      )



    return JSONResponse(content={"results": search_results})

