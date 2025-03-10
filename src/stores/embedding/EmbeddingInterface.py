from abc import ABC, abstractmethod
from typing import Dict, List, Any

class EmbeddingInterface(ABC):

    @abstractmethod
    def generate_embedding(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def set_embedding_settings(self, 
                               model_id,
                               max_input_token ):
        pass