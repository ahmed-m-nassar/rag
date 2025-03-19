from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str

    MAX_SIZE: int 
    ALLOWED_FILE_TYPES: List[str]  # List of allowed file types
    UPLOAD_DIR : str
    CHUNKS_DIR : str
    EMBEDDINGS_DIR : str
    EMBEDDING_MODELS_DIR : str
    RERANKING_MODELS_DIR : str

    VISUALIZATIONS_DIR : str

    MONGODB_CONNECTION : str
    MONGODB_DATABASE_NAME : str
    MONGODB_TEST_DATABASE_NAME : str

    
    # Vector DB
    VECTORDB_PATH  : str
    
    

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()