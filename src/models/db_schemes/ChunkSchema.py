from pydantic import BaseModel, Field, validator
from typing import Optional, List
from bson.objectid import ObjectId


class ChunkSchema(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    source: Optional[str] = Field(None)  # URL or document name
    chunk_index: int = Field(..., ge=0)  # Position in the document
    embedding: Optional[List[float]] = Field(None)  # Vector representation

    @validator("chunk_id")
    def validate_chunk_id(cls, value):
        if not value.isalnum():
            raise ValueError("chunk_id must be alphanumeric")
        return value

    class Config:
        arbitrary_types_allowed = True
