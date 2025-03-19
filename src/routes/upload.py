from fastapi import APIRouter, UploadFile, HTTPException, Request, status, Depends
from fastapi.responses import JSONResponse
import logging
import os

from controllers.FileController import FileController
from models.enums.ResponseEnum import ResponseSignal
from helpers.config import get_settings
from helpers.logger import get_logger  # Use centralized logging

upload_router = APIRouter(
    prefix="/api/v1/upload",
    tags=["api_v1", "upload"],
)

# Ensure the upload directory exists
UPLOAD_DIR = "assets/uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Logger
logger = get_logger(__name__)  

# Dependency Injection for FileController & Settings
def get_file_controller():
    return FileController()

@upload_router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    request: Request, 
    file: UploadFile, 
    file_controller: FileController = Depends(get_file_controller),
    settings=Depends(get_settings)
):
    try:
        # Validate the file
        await file_controller.validate_file(file)

        # Sanitize and generate unique filename
        safe_filename = await file_controller.sanitize_file_name(file)
        unique_safe_file_name = await file_controller.generate_unique_filename(
            file_directory=settings.UPLOAD_DIR, 
            file_name=safe_filename
        )

        # Save file
        await file_controller.save_file(file, UPLOAD_DIR, unique_safe_file_name)

        logger.info(f"File '{safe_filename}' uploaded successfully.")

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_name": unique_safe_file_name
            }
        )

    except HTTPException as e:
        logger.warning(f"File upload failed: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))

    except Exception as e:
        logger.error(f"Unexpected error during file upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ResponseSignal.UNEXPECTED_ERROR.value)
