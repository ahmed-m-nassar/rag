import requests
from typing import Dict, List, Any
from abc import ABC, abstractmethod
from stores.embedding.EmbeddingInterface import EmbeddingInterface
from openai import OpenAI

class OpenAIEmbeddingProvider(EmbeddingInterface):
    """Concrete implementation of EmbeddingInterface using OpenAI's API."""

    def __init__(self,
                 model_id: str,
                 max_input_token : int,
                 api_key : str=None,
                 api_url : str=None,
                 ):
        
        self.model_id = model_id
        self.max_input_token = max_input_token
        self.api_key = api_key
        self.api_url = api_url

        self.client = OpenAI(api_key=api_key)


    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates an embedding for the provided text.

        :param text: The input text to embed.
        :return: A list representing the embedding vector.
        """
        # Validate input text
        if not isinstance(text, str) or text.strip() == "":
            raise ValueError("Input text must be a non-empty string.")

        # Check token length (basic approximation)
        token_count = len(text.split())  # Use a tokenizer for better accuracy
        if token_count > self.max_input_token:
            raise ValueError(f"Input text exceeds max tokens ({token_count}/{self.max_input_token}). Please shorten it.")

        try:
            # Generate embedding using OpenAI client
            embedding = self.client.embeddings.create(
                input=text,
                model=self.model_id
            ).data[0].embedding

            return embedding

        except Exception as e:
            raise Exception(f"Error generating embedding: {e}")


    def set_embedding_settings(self, 
                               model_id,
                               max_input_token ):
        self.model_id = model_id
        self.max_input_token = max_input_token
