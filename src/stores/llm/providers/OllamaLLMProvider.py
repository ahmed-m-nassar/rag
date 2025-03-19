import os
import requests
from typing import List, Dict, Any
from stores.llm.LLMInterface import LLMInterface
from models.enums.LLMEnums import LLMEnums


class OllamaLLMProvider(LLMInterface):
    """Concrete implementation of LLMInterface for Ollama Server."""

    def __init__(self,
                 base_url: str ,
                 model: str,
                 system_prompt : str = None,):
        
        self.model = model
        self.system_prompt = system_prompt
        self.base_url = base_url
        self.params = {}

    def generate_response(self, prompt: str) -> str:
        """Generates a response from the Ollama LLM given a text prompt."""
        data = {
            "model": self.model,
            "stream": False,
            "messages": []
        }

        if self.system_prompt:
            data["messages"].append({"role": "system", "content": self.system_prompt})

        data["messages"].append({"role": "user", "content": prompt})
        
        response = requests.post(self.base_url, json=data)
        return response.json().get("message", {}).get("content", "No response received")

    def generate_chat_history_response(self, chat_history: List[Dict[str, str]]) -> str:
        """Generates a response based on a given chat history."""
        data = {
            "model": self.model,
            "stream": False,
            "messages": chat_history
        }
        response = requests.post(self.base_url, json=data)
        return response.json().get("message", {}).get("content", "No response received")

    def validate_token_limit(self, messages: List[str]):
        """Placeholder for token validation logic."""
        max_tokens = 4096  # Example limit, adjust as needed
        total_tokens = sum(len(msg.split()) for msg in messages)
        if total_tokens > max_tokens:
            raise ValueError(f"Token limit exceeded: {total_tokens}/{max_tokens}")

    def construct_chat_history(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Constructs chat history in the required format."""
        return [{"role": msg["role"], "content": msg["content"]} for msg in messages]

    def set_model_parameters(self, **kwargs: Any):
        """Updates model parameters dynamically."""
        self.params.update(kwargs)