import logging
from fastapi import UploadFile, HTTPException
from .BaseController import BaseController
from models.enums.ResponseEnum import ResponseSignal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileController(BaseController):
    
    def __init__(self):
        super().__init__()

    def validate_file_size(self, file: UploadFile):
        max_size = self.app_settings.MAX_SIZE * 1024 * 1024  # Convert MB to bytes
        if file.size > max_size:
            error_message = ResponseSignal.FILE_TOO_LARGE.value.format(self.app_settings.MAX_SIZE)
            logger.warning(f"File '{file.filename}' exceeds size limit ({file.size} bytes)")
            return {
                "status": "error",
                "message": error_message
            }
        return {"status": "success"}

    def validate_file_type(self, file: UploadFile):
        allowed_types = self.app_settings.ALLOWED_FILE_TYPES
        file_extension = file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_types:
            error_message = ResponseSignal.INVALID_FILE_TYPE.value.format(", ".join(allowed_types))
            logger.warning(f"Invalid file type for '{file.filename}'. Allowed: {allowed_types}")
            return {
                "status": "error",
                "message": error_message
            }
        return {"status": "success"}

    async def validate_file(self, file: UploadFile):
        logger.info(f"Validating file: {file.filename} ({file.size} bytes)")

        type_validation = self.validate_file_type(file)
        if type_validation["status"] == "error":
            raise HTTPException(status_code=400, detail=type_validation["message"])

        size_validation = self.validate_file_size(file)
        if size_validation["status"] == "error":
            raise HTTPException(status_code=400, detail=size_validation["message"])

        logger.info(f"File '{file.filename}' passed validation")
        return {"status": "success", "message": "File is valid"}
