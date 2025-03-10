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
                 ):
        
        self.model_id = model_id
        self.max_input_token = max_input_token
        self.api_key = api_key

        self.client = OpenAI(api_key=api_key)


    def generate_embedding(self, texts: List[str]) -> List[List[float]]:
        """
        Generates an embedding for the provided text.

        :param text: The input text to embed.
        :return: A list representing the embedding vector.
        """
        # Check token length (basic approximation)
        for text in texts:
            if len(text.split()) > self.max_input_token:
                raise ValueError(f"One of the inputs exceeds the max token limit of {self.max_input_token} tokens.")

        try:
            # Generate embedding using OpenAI client
            embedding = self.client.embeddings.create(
                input=text[0],
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
        