from bson import ObjectId
from typing import List, Optional
from models.db_schemes.ChunkSchema import ChunkSchema  # Assuming you have a FileSchema model
from models.BaseDataModel import BaseDataModel

class ChunkModel(BaseDataModel):

    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection