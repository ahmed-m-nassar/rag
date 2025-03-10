import os
from typing import Dict, List, Any
from abc import ABC, abstractmethod
from stores.embedding.EmbeddingInterface import EmbeddingInterface
from stores.embedding.EmbeddingEnum import HuggingFaceLocalModels
from sentence_transformers import SentenceTransformer
from helpers.config import get_settings

class HuggingFaceLocalEmbeddingProvider(EmbeddingInterface):
    def __init__(self, model_id: HuggingFaceLocalModels, max_input_token: int = 512):
        settings = get_settings()
        self.model_id = model_id
        self.max_input_token = max_input_token
        self.model = SentenceTransformer(os.path.join(settings.EMBEDDING_MODELS_DIR, model_id))  # Load model
        
    def generate_embedding(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts (List[str]): List of input texts.

        Returns:
            List[List[float]]: List of embedding vectors.
        """
        # Ensure each text does not exceed max tokens
        for text in texts:
            if len(text.split()) > self.max_input_token:
                raise ValueError(f"One of the inputs exceeds the max token limit of {self.max_input_token} tokens.")

        # Generate embeddings for the batch
        embeddings = self.model.encode(texts)
        return embeddings.tolist()  # Convert NumPy array to list

    def set_embedding_settings(self, model_id: HuggingFaceLocalModels, max_input_token: int):
        """
        Update embedding model and settings.

        Args:
            model_id (str): New model ID or local path.
            max_input_token (int): New max token limit.
        """
        self.model_id = model_id
        self.max_input_token = max_input_token
        self.model = SentenceTransformer(model_id)  # Reload model