from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId


class FileSchema(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    file_id: str = Field(..., min_length=1)

    @validator('file_id')
    def validate_file_id(cls, value):
        if not value.isalnum():
            raise ValueError('file_id must be alphanumeric')
        
        return value

    class Config:
        arbitrary_types_allowed = True

