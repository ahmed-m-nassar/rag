from fastapi import APIRouter, UploadFile,HTTPException,Request
from controllers.FileController  import FileController
from models.FileModel import FileModel
from models.db_schemes.FileSchema import FileSchema
import os


file_router = APIRouter(
    prefix="/api/v1/file",
    tags=["api_v1", "file"],
)

UPLOAD_DIR = "assets/uploaded_files"  # Directory where files will be saved
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure the directory exists

@file_router.post("/upload/")
async def upload_file(file: UploadFile):
    file_controller = FileController()
    
    # Validate the file
    try:
        await file_controller.validate_file(file)
    except HTTPException as e:
        return {"status": "error", "message": e.detail}  # Return validation error

    # Save the file (Optional: Implement storage logic)
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    return {
        "status": "success",
        "message": "File uploaded successfully",
        "filename": file.filename,
        "path": file_location
    }


@file_router.post("/test/")
async def test(request : Request , file: FileSchema):
    
    file_dict = file.dict(by_alias=True, exclude={"id"})
    result = await request.app.test_db_connection["file"].insert_one(file_dict)
    print(result)
    #request.app.db_connection
    