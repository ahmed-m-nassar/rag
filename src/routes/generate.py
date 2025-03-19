from fastapi import APIRouter, Request, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from controllers.NLPController import NLPController
from models.enums.LLMEnums import LLMEnums
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.llm.LLMEnum import LLMsProviders

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

generate_router = APIRouter(
    prefix="/api/v1/generate",
    tags=["api_v1", "generate"],
)

# ✅ Pydantic Model for Request Body
class GenerateRequest(BaseModel):
    query: str = Field(..., description="User query for LLM generation.")
    docs: List[str] = Field(..., description="List of documents to provide context.")
    provider: LLMsProviders = Field(..., description="LLM provider to use.")
    base_url: str = Field(..., description="Base URL of the LLM service.")
    model_id: str = Field(..., description="Model identifier for the LLM provider.")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt (if any).")

def get_nlp_controller() -> NLPController:
    """Dependency injection for NLPController instance."""
    return NLPController()

@generate_router.post("/")
async def generate_response(
    request: Request,
    generate_request: GenerateRequest,
    api_key: Optional[str] = Header(None, alias="api-key"),
    nlp_controller: NLPController = Depends(get_nlp_controller),
):
    """
    Generates a response using an LLM based on the given query and document context.

    Returns:
        JSONResponse containing the generated response.
    """

    try:
        # Set default system prompt if not provided
        system_prompt = generate_request.system_prompt or LLMEnums.SYSTEM_PROMPT.value

        # Initialize LLM provider
        llm_client = LLMProviderFactory().get_llm(
            provider=generate_request.provider,
            base_url=generate_request.base_url,
            model_id=generate_request.model_id,
            api_key=api_key,
            system_prompt=system_prompt
        )

        if not llm_client:
            logger.error(f"Failed to initialize LLM provider: {generate_request.provider}")
            raise HTTPException(status_code=400, detail="Invalid LLM provider configuration.")

        # Generate formatted query
        query = await nlp_controller.create_generation_query(
            question=generate_request.query, 
            docs=generate_request.docs
        )

        # Generate response from LLM
        response = await nlp_controller.generate_response(llm_client=llm_client, query=query)

        logger.info("LLM response generated successfully.")
        return {"response": response}

    except HTTPException as http_exc:
        raise http_exc  # Propagate known errors

    except Exception as e:
        logger.error(f"Unexpected error during LLM generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
