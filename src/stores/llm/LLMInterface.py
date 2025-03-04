from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMInterface(ABC):
    """Abstract base class for Large Language Model (LLM) operations."""

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generates a response from the LLM given a text prompt."""
        pass
    
    @abstractmethod
    def generate_chat_history_response(self, chat_history: List[Dict[str, str]]) -> str:
        """Generates a response based on a given chat history."""
        pass
    
    @abstractmethod
    def validate_token_limit(self, messages: List[str]):
        """Validates if the input messages exceed the max token limit."""
        pass
    
    @abstractmethod
    def construct_chat_history(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Constructs chat history messages in a structured format."""
        pass
    
    @abstractmethod
    def set_model_parameters(self, **kwargs: Any):
        """Updates model parameters dynamically."""
        pass
