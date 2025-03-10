import os
import json
import logging
from .BaseController import BaseController
from stores.vectordb.VectorDBInterface import VectorDBInterface
from stores.embedding.EmbeddingInterface import EmbeddingInterface
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchController(BaseController):
    
    def __init__(self):
        super().__init__()

    async def semantic_search(self , 
                              vectordb : VectorDBInterface ,
                              embedding_client :EmbeddingInterface,
                              collection_name : str ,
                              query : str ,
                              n_results : str ):
        embeddings = embedding_client.generate_embedding(texts=[query])
        return vectordb.query_embeddings(collection_name=collection_name ,
                                         n_results=n_results , 
                                         embeddings=embeddings ).get('documents', [])[0]

