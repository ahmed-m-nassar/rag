from abc import ABC, abstractmethod
from typing import List, Tuple

class RerankingInterface(ABC):
    """Abstract base class for reranking models."""

    @abstractmethod
    def rerank(self, query: str, documents: list) -> list:
        """Given a query and multiple documents, return a ranked list of (doc, score)."""
        pass
