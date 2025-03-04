import requests
from typing import Dict, List, Any
from abc import ABC, abstractmethod
from stores.embedding.EmbeddingInterface import EmbeddingInterface

class HuggingFaceAPIProvider(EmbeddingInterface):
    def __init__(self, model_id: str, api_key: str, max_input_token: int = 512):
        self.model_id = model_id
        self.api_key = api_key
        self.max_input_token = max_input_token
        self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings using Hugging Face Inference API."""

        # Ensure text length does not exceed max tokens
        if len(text.split()) > self.max_input_token:
            raise ValueError(f"Input text exceeds max token limit of {self.max_input_token} tokens.")

        # Prepare request payload
        payload = {"inputs": text}

        # Make API request
        response = requests.post(self.api_url, headers=self.headers, json=payload)

        # Check for errors
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}, {response.text}")

        # Return the embedding vector
        return response.json()[0]

    def set_embedding_settings(self, model_id: str, max_input_token: int):
        """Update embedding model and settings."""
        self.model_id = model_id
        self.max_input_token = max_input_token
        self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"