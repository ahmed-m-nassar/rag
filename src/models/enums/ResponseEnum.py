from enum import Enum

class ResponseSignal(Enum):

    FILE_VALIDATED_SUCCESS = "file_validate_successfully"
    INVALID_FILE_TYPE = "Invalid file type. Allowed types: {}"
    FILE_TOO_LARGE = "File size exceeds the limit of {}MB"
    FILE_UPLOAD_SUCCESS = "file_upload_success"
    FILE_UPLOAD_FAILED = "file_upload_failed"
    PROCESSING_SUCCESS = "processing_success"
    PROCESSING_FAILED = "processing_failed"
    CHUNKS_EMBEDDED_SUCCESSFULLY = "Chunks embedded successfully"