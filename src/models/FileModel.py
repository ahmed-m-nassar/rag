from bson import ObjectId
from typing import List, Optional
from models.db_schemes.FileSchema import FileSchema  # Assuming you have a FileSchema model
from models.BaseDataModel import BaseDataModel

class FileModel(BaseDataModel):

    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection

    async def insert_file(self, file: FileSchema):
        file_dict = file.dict(by_alias=True, exclude={"id"})
        result = await self.db_connection["file"].insert_one(file_dict)
        return str(result.inserted_id)  # Return the inserted document's ID as a string

    async def get_files(self) -> List[FileSchema]:
        """Retrieve all files from the database."""
        cursor = self.db_connection["file"].find({})
        files = await cursor.to_list(length=None)  # Convert cursor to a list
        return [FileSchema(**file, id=str(file["_id"])) for file in files]  # Convert ObjectId to string

    async def get_file_with_id(self, file_id: str) -> Optional[FileSchema]:
        """Retrieve a single file by its ID."""
        file_data = await self.db_connection["file"].find_one({"_id": ObjectId(file_id)})
        if file_data:
            return FileSchema(**file_data, id=str(file_data["_id"]))  # Convert ObjectId to string
        return None  # Return None if the file is not found
