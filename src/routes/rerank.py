from fastapi import APIRouter,Request
from fastapi.responses import JSONResponse
import logging
import os
from controllers.NLPController  import NLPController
from stores.reranking.RerankingProviderFactory import RerankerProviderFactory
from helpers.config import get_settings
from models.enums.SearchTechniqueEnum import SearchTechniqueEnums
from stores.reranking.RerankingEnum import RerankingModelsProvidersEnums
from fastapi import APIRouter,Request ,Header , Body
from stores.embedding.EmbeddingEnum import EmbeddingEnum
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rerank_router = APIRouter(
    prefix="/api/v1/rerank",
    tags=["api_v1", "rerank"],
)

@rerank_router.post("/")
async def rerank(
    request: Request,
    query: str = Body(...),
    docs: list = Body(...),
    provider: RerankingModelsProvidersEnums = Body(...),
    model_id: str = Body(...),
    api_key: Optional[str] = Header(None, alias="api-key")
):
    nlp_controller = NLPController()

    # Initialize reranker provider
    reranker_client = RerankerProviderFactory().get_reranker(provider=provider , 
                                                                       model_id=model_id ,
                                                                       api_key=api_key)

    reranking_results = await nlp_controller.rerank(query=query,
                                                 docs=docs,
                                                 reranking_client=reranker_client)

    return JSONResponse(content={"results": reranking_results})

from fastapi import APIRouter, Request, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from controllers.NLPController import NLPController
from stores.reranking.RerankingProviderFactory import RerankerProviderFactory
from models.enums.SearchTechniqueEnum import SearchTechniqueEnums
from stores.reranking.RerankingEnum import RerankingModelsProvidersEnums

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rerank_router = APIRouter(
    prefix="/api/v1/rerank",
    tags=["api_v1", "rerank"],
)

# ✅ Pydantic Model for Request Parameters
class RerankRequest(BaseModel):
    query: str = Field(..., description="User query for reranking.")
    docs: List[str] = Field(..., description="List of documents to rerank.")
    provider: RerankingModelsProvidersEnums = Field(..., description="Reranking provider to use.")
    model_id: str = Field(..., description="Model identifier for reranker.")

def get_nlp_controller() -> NLPController:
    """Dependency injection for NLPController instance."""
    return NLPController()

@rerank_router.post("/")
async def rerank(
    request: Request,
    rerank_request: RerankRequest,  # 🔹 Use Pydantic model for request validation
    api_key: Optional[str] = Header(None, alias="api-key"),
    nlp_controller: NLPController = Depends(get_nlp_controller),
):
    """
    Handles document reranking based on relevance to a query.

    - Uses a specified reranking model to sort `docs` based on `query`.
    - Utilizes different providers to perform reranking.

    Returns:
        JSONResponse containing reranked results.
    """

    # Initialize reranker provider
    reranker_client = RerankerProviderFactory().get_reranker(
        provider=rerank_request.provider,
        model_id=rerank_request.model_id,
        api_key=api_key
    )

    if not reranker_client:
        logger.error(f"Invalid reranking provider: {rerank_request.provider}")
        raise HTTPException(status_code=400, detail="Invalid reranking provider.")

    try:
        reranking_results = await nlp_controller.rerank(
            query=rerank_request.query,
            docs=rerank_request.docs,
            reranking_client=reranker_client
        )

        logger.info(f"Reranking completed for provider: {rerank_request.provider}, results: {len(reranking_results)}")
        return JSONResponse(content={"results": reranking_results})

    except Exception as e:
        logger.error(f"Error during reranking: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
