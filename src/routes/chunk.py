from fastapi import APIRouter,Request
from fastapi.responses import JSONResponse
import logging
from controllers.FileController  import FileController
from controllers.ChunkController  import ChunkController
from helpers.config import get_settings
from models.enums.ChunkingEnum import ChunkingEnum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

chunk_router = APIRouter(
    prefix="/api/v1/chunk",
    tags=["api_v1", "file"],
)

@chunk_router.get("/")
async def chunk_file(request : Request , 
                     file_name : str ,
                     chunking_method: ChunkingEnum = ChunkingEnum.RECURSIVE,  # Default to RECURSIVE
                     chunk_size: int = 100, 
                     chunk_overlap: int = 20, 
                     ):

    file_controller = FileController()
    chunk_controller = ChunkController()

    settings = get_settings()
    file_content = await file_controller.load_file_content(file_directory=settings.UPLOAD_DIR , file_name=file_name)
    
    chunks = await chunk_controller.chunk_text(method= chunking_method,
                                               text=file_content,
                                               chunk_size=chunk_size,
                                               chunk_overlap=chunk_overlap)
    
    await chunk_controller.save_chunks(chunks=chunks , file_directory=settings.CHUNKS_DIR)
    chunks = await chunk_controller.load_chunks(file_directory=settings.CHUNKS_DIR)

    sample_chunks = chunks[:3] if len(chunks) > 3 else chunks
    return JSONResponse(
                    content={
                        "sample_chunks": [chunk for chunk in sample_chunks], 
                        "total_chunks": len(chunks),
                    }
                )
