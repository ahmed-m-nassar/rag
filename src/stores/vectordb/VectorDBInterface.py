from abc import ABC, abstractmethod

class VectorDBInterface(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def collection_exists_flg(self ,collection_name):
        pass

    @abstractmethod
    def create_collection(self, collection_name):
        pass
        
    @abstractmethod
    def get_collection(self, collection_name):
        pass
        
    @abstractmethod
    def delete_collection(self, collection_name):
        pass

    @abstractmethod
    def add_vectors(self, documents: list, embeddings: list, metadatas: list = None, ids: list = None, collection_name: str = "default", batch_size: int = 100):
        pass

    @abstractmethod
    def query_embeddings(self, embeddings : list , n_results , collection_name):
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str):
        pass