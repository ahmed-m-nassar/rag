from .providers.ChromaDBProvider import ChromaDBProvider
from .VectorDBEnum import VectorDBEnum
class VerctorDBProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):
        if provider == VectorDBEnum.CHROMA_DB.value:
            return ChromaDBProvider(
                path = self.config.VECTORDB_PATH,
            )