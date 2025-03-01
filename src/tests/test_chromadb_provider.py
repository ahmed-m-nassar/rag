import os
import pytest
from stores.vectordb.providers.ChromaDBProvider import ChromaDBProvider

@pytest.fixture
def temp_db_path(tmp_path):
    """Fixture to create a temporary directory for ChromaDB storage."""
    return str(tmp_path / "chromadb")

def test_chromadb_provider_initialization(temp_db_path):
    """Test that ChromaDBProvider initializes and creates the path if it doesn't exist."""
    provider = ChromaDBProvider(path=temp_db_path)
    
    # Check if the directory is created
    assert os.path.exists(temp_db_path), "ChromaDB path should be created."

def test_chromadb_connect_disconnect(temp_db_path):
    """Test that ChromaDBProvider can connect and disconnect."""
    provider = ChromaDBProvider(path=temp_db_path)
    
    # Connect to ChromaDB
    provider.connect()
    assert provider.client is not None, "ChromaDB client should be initialized."

    # Disconnect from ChromaDB
    provider.disconnect()
    assert provider.client is None, "ChromaDB client should be None after disconnect."

def test_create_collection(temp_db_path):
    """Test creating a collection in ChromaDB."""
    provider = ChromaDBProvider(path=temp_db_path)
    provider.connect()

    collection_name = "test_collection"
    provider.create_collection(collection_name)

    # Verify collection exists
    assert provider.collection_exists_flg(collection_name), "Collection should exist."

def test_add_vectors(temp_db_path):
    """Test adding vectors to a ChromaDB collection."""
    provider = ChromaDBProvider(path=temp_db_path)
    provider.connect()

    collection_name = "test_vectors"
    provider.create_collection(collection_name)

    documents = ["Test doc 1", "Test doc 2"]
    embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    metadatas = [{"meta": "data1"}, {"meta": "data2"}]
    ids = ["1", "2"]

    provider.add_vectors(documents, embeddings, metadatas, ids, collection_name)

    # Check if vectors were added
    info = provider.get_collection_info(collection_name)
    print(info)
    assert info["num_vectors"] == 2, "Two vectors should be added."


def test_add_more_vectors(temp_db_path):
    """Test adding more vectors to an existing ChromaDB collection."""
    provider = ChromaDBProvider(path=temp_db_path)
    provider.connect()

    collection_name = "test_vectors"
    provider.create_collection(collection_name)

    # Initial vectors
    documents = ["Test doc 1", "Test doc 2"]
    embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    metadatas = [{"meta": "data1"}, {"meta": "data2"}]
    ids = ["1", "2"]

    provider.add_vectors(documents, embeddings, metadatas, ids, collection_name)

    # Get the initial count
    initial_info = provider.get_collection_info(collection_name)
    initial_count = initial_info["num_vectors"]
    print("Initial Collection Info:", initial_info)

    # Adding new vectors
    new_documents = ["Test doc 3", "Test doc 4"]
    new_embeddings = [[0.7, 0.8, 0.9], [1.0, 1.1, 1.2]]
    new_metadatas = [{"meta": "data3"}, {"meta": "data4"}]
    new_ids = ["3", "4"]

    provider.add_vectors(new_documents, new_embeddings, new_metadatas, new_ids, collection_name)

    # Get the updated count
    updated_info = provider.get_collection_info(collection_name)
    updated_count = updated_info["num_vectors"]
    print("Updated Collection Info:", updated_info)

    # Assert the count increased correctly
    assert updated_count == initial_count + len(new_documents), "Vector count should increase by the number of new vectors."
