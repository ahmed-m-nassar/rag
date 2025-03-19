from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import logging
import os
from controllers.FileController import FileController
from controllers.ChunkController import ChunkController
from helpers.config import get_settings
from models.enums.ChunkingEnum import ChunkingEnum
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI router
chunk_router = APIRouter(
    prefix="/api/v1/chunk",
    tags=["api_v1", "chunk"],
)

# Dependency injection function for FileController
def get_file_controller() -> FileController:
    return FileController()

# Dependency injection function for ChunkController
def get_chunk_controller() -> ChunkController:
    return ChunkController()

class ChunkRequest(BaseModel):
    file_name: str = Field(..., min_length=1, description="The name of the file to be chunked")
    chunking_method: ChunkingEnum = ChunkingEnum.RECURSIVE  # Default value
    chunk_size: int = Field(100, gt=0, description="Size of each chunk, must be > 0")
    chunk_overlap: int = Field(20, ge=0, description="Size of chunk overlap, must be ≥ 0")

@chunk_router.post("/")
async def chunk_file(
    request: Request,
    request_data: ChunkRequest,
    file_controller: FileController = Depends(get_file_controller),
    chunk_controller: ChunkController = Depends(get_chunk_controller),
):
    """
    Splits a file into chunks based on the specified chunking method.

    Parameters:
    - file_name (str): Name of the file to chunk.
    - chunking_method (ChunkingEnum): Chunking method (default: RECURSIVE).
    - chunk_size (int): Size of each chunk (default: 100).
    - chunk_overlap (int): Overlapping size between chunks (default: 20).

    Returns:
    - JSONResponse: Contains sample chunks and total chunk count.
    """
    settings = get_settings()

    try:
        # Load file content
        logger.info(f"Loading file: {request_data.file_name} from {settings.UPLOAD_DIR}")
        file_content = await file_controller.load_file_content(
            file_directory=settings.UPLOAD_DIR, file_name=request_data.file_name
        )

        if not file_content:
            logger.warning(f"File {request_data.file_name} is empty.")
            raise HTTPException(status_code=400, detail=f"File '{request_data.file_name}' is empty.")

        # Chunk text
        logger.info(f"Chunking file using method: {request_data.chunking_method.name}")
        chunks = await chunk_controller.chunk_text(
            method=request_data.chunking_method, text=file_content, chunk_size=request_data.chunk_size, chunk_overlap=request_data.chunk_overlap
        )

        if not chunks:
            logger.warning(f"No chunks generated for file: {request_data.file_name}")
            raise HTTPException(status_code=400, detail="Chunking failed, no chunks were generated.")

        # Save chunks to a file
        chunk_file_name = os.path.splitext(request_data.file_name)[0] + "_chunks.json"
        logger.info(f"Saving chunks to {chunk_file_name} in {settings.CHUNKS_DIR}")
        await chunk_controller.save_chunks(
            chunks=chunks, file_directory=settings.CHUNKS_DIR, file_name=chunk_file_name
        )

        # Return sample chunks
        sample_chunks = chunks[:3] if len(chunks) > 3 else chunks
        return JSONResponse(
            content={
                "message": "Chunking successful",
                "sample_chunks": sample_chunks,
                "total_chunks": len(chunks),
            }
        )

    except FileNotFoundError:
        logger.error(f"File not found: {request_data.file_name}")
        raise HTTPException(status_code=400, detail=f"File '{request_data.file_name}' not found.")

    except ValueError as e:
        logger.error(f"Invalid value encountered: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.exception(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error. Please try again later.")
