from stores.vectordb.VectorDBInterface import VectorDBInterface
import chromadb
import logging
import numpy as np
import os

class ChromaDBProvider(VectorDBInterface):
    
    def __init__(self, path: str):
        """
        Initialize ChromaDB provider and ensure the given path exists.

        Args:
        - path (str): Path where the ChromaDB data should be stored.
        """
        self.client_path = path

        # Ensure the directory exists
        if not os.path.exists(self.client_path):
            os.makedirs(self.client_path, exist_ok=True)
            logging.info(f"Path '{self.client_path}' did not exist. Created successfully.")
        else:
            logging.info(f"Using existing path: {self.client_path}")
        
    def connect(self):
        """
        Establish connection with ChromaDB.
        """
        self.client = chromadb.PersistentClient(self.client_path)
        logging.info("Connected to ChromaDB.")
    
    def disconnect(self):
        """
        Close the ChromaDB connection.
        """
        self.client = None
        logging.info("Disconnected from ChromaDB.")
    
    def collection_exists_flg(self, collection_name: str) -> bool:
        """
        Check if a collection exists.
        """
        try:
            collection = self.client.get_collection(collection_name)
            return collection is not None
        except Exception:
            return False

    def create_collection(self, collection_name: str):
        """
        Create a new collection if it doesn't exist.
        """
        if not self.collection_exists_flg(collection_name):
            self.client.create_collection(name=collection_name)
            logging.info(f"Collection '{collection_name}' created.")
        else:
            logging.info(f"Collection '{collection_name}' already exists.")
    
    def get_collection(self, collection_name: str):
        """
        Retrieve an existing collection.
        """
        if self.collection_exists_flg(collection_name):
            return self.client.get_collection(name=collection_name)
        logging.warning(f"Collection '{collection_name}' does not exist.")
        return None

    def delete_collection(self, collection_name: str):
        """
        Delete a collection.
        """
        if self.collection_exists_flg(collection_name):
            self.client.delete_collection(name=collection_name)
            logging.info(f"Collection '{collection_name}' deleted.")
        else:
            logging.warning(f"Collection '{collection_name}' not found.")


    def add_vectors(self, documents: list, embeddings: list, metadatas: list = None, ids: list = None, collection_name: str = "default", batch_size: int = 100):
        """
        Add vectors (embeddings) to a collection in batches with dimension validation against existing embeddings.

        Args:
        - documents (list): List of text documents.
        - embeddings (list): List of embeddings (vectors).
        - metadatas (list, optional): List of metadata dictionaries. If None, defaults to empty dictionaries.
        - ids (list, optional): List of unique IDs. If None, generates sequential numeric IDs.
        - collection_name (str): Target collection name.
        - batch_size (int): Number of embeddings per batch (default=100).
        """
        collection = self.get_collection(collection_name)
        if not collection:
            logging.error(f"Cannot add vectors. Collection '{collection_name}' not found.")
            return

        # Ensure metadatas and ids are provided
        if metadatas is None or not all(isinstance(m, dict) and m for m in metadatas): 
            metadatas = [{"default_key": "default_value"} for _ in range(len(documents))]  # Add a dummy key-value pair


        if ids is None:
            ids = [str(i) for i in range(len(documents))]  # Generate numeric string IDs

        # Step 1: Check existing embeddings in collection
        existing_data = collection.query(query_embeddings=[[0] * len(embeddings[0])], n_results=1)  # Dummy query

        if existing_data and 'embeddings' in existing_data and existing_data['embeddings']:
            existing_dim = len(existing_data['embeddings'][0])  # Get the stored embedding dimension
        else:
            existing_dim = len(embeddings[0])  # Use the first new embedding's dimension if collection is empty

        # Step 2: Validate new embeddings against expected dimension
        embedding_dims = [len(emb) for emb in embeddings]
        unique_dims = set(embedding_dims)

        if len(unique_dims) > 1 or existing_dim not in unique_dims:
            logging.error(f"Inconsistent embedding dimensions found: {unique_dims}. Expected dimension: {existing_dim}.")
            return

        logging.info(f"Embedding dimension check passed. Expected dimension: {existing_dim}")

        # Step 3: Insert embeddings in batches
        total_vectors = len(embeddings)
        for i in range(0, total_vectors, batch_size):
            batch_documents = documents[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]

            collection.add(
                embeddings=batch_embeddings,
                metadatas=batch_metadatas,
                ids=batch_ids,
                documents=batch_documents
            )
            logging.info(f"Inserted batch {i // batch_size + 1} ({len(batch_embeddings)} vectors) into '{collection_name}'.")

        logging.info(f"Successfully added {total_vectors} vectors to '{collection_name}' in batches of {batch_size}.")
        
            
    def query_embeddings(self, embeddings: list, n_results: int, collection_name: str):
        """
        Query similar embeddings from the collection.
        """
        collection = self.get_collection(collection_name)
        if collection:
            results = collection.query(query_embeddings=embeddings, n_results=n_results)
            return results
        logging.warning(f"Cannot query. Collection '{collection_name}' not found.")
        return None


    def get_collection_info(self, collection_name: str):
        """
        Retrieve metadata and number of embeddings stored in a collection.
        """
        collection = self.get_collection(collection_name)
        sample_data = collection.get(include=['embeddings', 'documents', 'metadatas'] , limit=3)
        if collection:
            try:
                count = collection.count()  # Get total number of embeddings
                info = {
                    "collection_name": collection_name,
                    "num_vectors": count,
                    "sample": {
                        "documents": sample_data.get("documents", []),
                        "embeddings": sample_data.get("embeddings", []),
                        "metadatas": sample_data.get("metadatas", []),
                        "ids": sample_data.get("ids", [])
                    }
                }
                return info
            except Exception as e:
                logging.error(f"Error fetching collection info: {e}")
                return None
        logging.warning(f"Collection '{collection_name}' does not exist.")
        return None