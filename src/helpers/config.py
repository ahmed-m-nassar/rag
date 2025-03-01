from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str

    MAX_SIZE: int 
    ALLOWED_FILE_TYPES: List[str]  # List of allowed file types
    
    MONGODB_CONNECTION : str
    MONGODB_DATABASE_NAME : str
    MONGODB_TEST_DATABASE_NAME : str

    
    # Vector DB
    VECTORDB_CLIENT  : str
    VECTORDB_PATH  : str
    
    class Config:
        env_file = ".env"

def get_settings():
    return Settings()