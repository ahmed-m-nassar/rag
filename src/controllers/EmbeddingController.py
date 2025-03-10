import os
import json
import logging
from .BaseController import BaseController

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingController(BaseController):
    
    def __init__(self):
        super().__init__()

    async def save_embeddings(self, file_directory: str , file_name : str, embeddings: list[list[float]]):
        """Save embeddings to a local JSON file."""
        try:
            embedding_file_path = os.path.join(file_directory, file_name)
            with open(embedding_file_path, "w") as f:
                json.dump(embeddings, f)
            logger.info(f"Embeddings saved successfully to {embedding_file_path}")
        except Exception as e:
            logger.error(f"Failed to save embeddings: {e}")

    async def load_embeddings(self, file_directory: str , file_name : str) -> list[list[float]]:
        """Load embeddings from a local JSON file."""
        embedding_file_path = os.path.join(file_directory, file_name)
        if not os.path.exists(embedding_file_path):
            logger.error(f"File {embedding_file_path} does not exist.")
            return []
        
        try:
            with open(embedding_file_path, "r") as f:
                embeddings = json.load(f)
            logger.info(f"Embeddings loaded successfully from {embedding_file_path}")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to load embeddings: {e}")
            return []
