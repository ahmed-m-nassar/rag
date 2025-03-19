from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import FileResponse
import os
import logging
import numpy as np
from controllers.NLPController import NLPController
from helpers.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI router
visualize_router = APIRouter(
    prefix="/api/v1/visualize",
    tags=["api_v1", "visualize"],
)

# Dependency Injection for NLP Controller
def get_nlp_controller() -> NLPController:
    return NLPController()

# Dependency Injection for Settings
def get_settings_config():
    return get_settings()

@visualize_router.get("/")
async def get_visualizations(
    request: Request, 
    file_name: str, 
    nlp_controller: NLPController = Depends(get_nlp_controller),
    settings = Depends(get_settings_config)
):
    """
    Generates an interactive visualization of text embeddings.

    Parameters:
    - file_name (str): The name of the file uploaded.

    Returns:
    - HTML visualization file response.
    """

    logger.info(f"Generating visualization for file: {file_name}")

    try:
        collection_name = os.path.splitext(file_name)[0]

        # Fetch embeddings and documents from vector database
        data = request.app.vectordb.get_collection(collection_name).get(include=['embeddings', 'documents'])

        chunks = data.get("documents", [])
        embeddings = data.get("embeddings", [])

        if len(chunks) == 0 or (isinstance(embeddings, np.ndarray) and embeddings.size == 0):
            logger.warning(f"No embeddings or documents found for file: {file_name}")
            raise HTTPException(status_code=400, detail="No embeddings or documents available for visualization.")

        # Generate visualization file
        visualization_file_path = await nlp_controller.create_interactive_embeddings(
            vectors=embeddings, 
            perplexity=5, 
            labels=chunks, 
            file_directory=settings.VISUALIZATIONS_DIR, 
            file_name=f"{collection_name}_viz.html"
        )

        logger.info(f"Visualization created successfully: {visualization_file_path}")

        return FileResponse(
            visualization_file_path, 
            media_type="text/html", 
            filename=os.path.basename(visualization_file_path)
        )

    except Exception as e:
        logger.exception(f"Error generating visualization for file {file_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while generating visualization.")
