from .BaseDataModel import BaseDataModel
from .db_schemes.FileSchema import FileSchema

class FileModel(BaseDataModel):

    def __init__(self , db_connection):
        super().__init__()
        self.db_connection = db_connection

    async def insert_file(self , file : FileSchema):
        file_dict = file.dict(by_alias=True, exclude={"id"})
        return await self.db_connection["file"].insert_one(file_dict)

    async def get_files(self):
        pass

    async def get_file_with_id(self , file_id : str):
        pass