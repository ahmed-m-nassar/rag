from fastapi import APIRouter, UploadFile,HTTPException,Request , status
from fastapi.responses import JSONResponse
import logging
from controllers.FileController  import FileController
from models.enums.ResponseEnum import ResponseSignal
from helpers.config import get_settings

import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

upload_router = APIRouter(
    prefix="/api/v1/upload",
    tags=["api_v1", "upload"],
)

UPLOAD_DIR = "assets/uploaded_files"  # Directory where files will be saved
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure the directory exists

@upload_router.post("/")
async def upload_file(request : Request , file: UploadFile):

    settings = get_settings()
    file_controller = FileController()

    # Validate the file
    try:
        await file_controller.validate_file(file)
    except HTTPException as e:
        return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                            "message": e.detail
                        }
                    )
    
    # Sanitize file name
    safe_filename = await file_controller.sanitize_file_name(file)

    # Generate unique santized file name
    unique_safe_file_name = await file_controller.generate_unique_filename(file_directory= settings.UPLOAD_DIR, file_name=safe_filename)

    # Save file
    await file_controller.save_file(file , UPLOAD_DIR , unique_safe_file_name)

    logger.info(f"File '{safe_filename}' uploaded successfully.")

    
    return JSONResponse(
                        content={
                            "message": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                            "file_name" : unique_safe_file_name
                        }
                    )



