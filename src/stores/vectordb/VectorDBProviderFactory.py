from .providers.ChromaDBProvider import ChromaDBProvider
from .VectorDBEnum import VectorDBEnum
class VectorDBProviderFactory:
    def __init__(self ):
        pass

    def create(self, provider: str , path : str):
        if provider == VectorDBEnum.CHROMA_DB.value:
            return ChromaDBProvider(
                path = path,
            )