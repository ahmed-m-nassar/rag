from fastapi import APIRouter, UploadFile,HTTPException,Request , status
from fastapi.responses import JSONResponse
import logging
from controllers.FileController  import FileController
from models.FileModel import FileModel
from models.db_schemes.FileSchema import FileSchema
from models.db_schemes.ChunkSchema import ChunkSchema
from models.enums.ResponseEnum import ResponseSignal
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file_router = APIRouter(
    prefix="/api/v1/file",
    tags=["api_v1", "file"],
)

UPLOAD_DIR = "assets/uploaded_files"  # Directory where files will be saved
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure the directory exists

@file_router.post("/upload/")
async def upload_file(request : Request , file: UploadFile):
    
    file_controller = FileController()
    file_model = FileModel(request.app.test_db_connection)

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
    
    # Save file metadata in db
    file_metadata = FileSchema(
                        file_id=file.filename,
                        file_name=file.filename,
                        file_size=file.size,
                        file_type=file.filename.split('.')[-1].lower()
                    )
    file_model.insert_file(file_metadata)
    logger.info(f"File inserted in DB: ID={file_metadata.file_id}, Name={file_metadata.file_name}, Size={file_metadata.file_size} bytes, Type={file_metadata.file_type}")


    # Save the file (Optional: Implement storage logic)
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    return JSONResponse(
                        content={
                            "message": ResponseSignal.FILE_UPLOAD_SUCCESS
                        }
                    )



@file_router.post("/chunk/")
async def upload_file(request : Request , file: UploadFile):
    
    file_controller = FileController()
    file_model = FileModel(request.app.test_db_connection)


@file_router.post("/test/")
async def test(request : Request ):

    loader = PyPDFLoader("assets/uploaded_files/cv.pdf")
    file_content = ""
    async for page in loader.alazy_load():
        file_content = file_content + page.page_content 
        
    text_splitter = RecursiveCharacterTextSplitter(
                            # Set a really small chunk size, just to show.
                            chunk_size=100,
                            chunk_overlap=20,
                            length_function=len,
                            is_separator_regex=False,
                        )
    chunks = text_splitter.create_documents([file_content])

    chunk_objects = [
        ChunkSchema(
            chunk_id=f"chunk{i}",
            content=chunk.page_content,
            chunk_index=i
        )
        for i, chunk in enumerate(chunks)
    ]
    print(chunk_objects)
    #request.app.db_connection
    