from stores.embedding.providers.OpenAIEmbeddingProvider import OpenAIEmbeddingProvider
import os
import pytest
from unittest.mock import MagicMock
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

@pytest.fixture
def openai_provider(mocker):
    """Fixture to create an OpenAIEmbeddingProvider with a mocked API client."""
    mock_client = MagicMock()
    mocker.patch("stores.embedding.providers.OpenAIEmbeddingProvider.OpenAI", return_value=mock_client)

    provider = OpenAIEmbeddingProvider(
        model_id="text-embedding-3-small",
        max_input_token=512,
        api_key=os.getenv("EMBEDDING_API_KEY")  # Load from .env
    )

    provider.client = mock_client  # Use the mocked client
    return provider

def test_generate_embedding_valid_text(openai_provider):
    """Test embedding generation for valid input text."""
    openai_provider.client.embeddings.create.return_value.data = [{"embedding": [0.1, 0.2, 0.3]}]

    embedding = openai_provider.generate_embedding("Hello, world!")
    assert isinstance(embedding, list)
    assert len(embedding) == 3  # Mocked response has 3 values
    assert embedding == [0.1, 0.2, 0.3]

def test_generate_embedding_empty_text(openai_provider):
    """Test that empty input raises ValueError."""
    with pytest.raises(ValueError, match="Input text must be a non-empty string"):
        openai_provider.generate_embedding("")

def test_generate_embedding_exceeds_max_tokens(openai_provider):
    """Test that input exceeding max tokens raises ValueError."""
    long_text = "word " * 600  # More than max_input_token=512
    with pytest.raises(ValueError, match="Input text exceeds max tokens"):
        openai_provider.generate_embedding(long_text)

def test_generate_embedding_api_error(openai_provider):
    """Test handling of API errors."""
    openai_provider.client.embeddings.create.side_effect = Exception("API error")
    with pytest.raises(Exception, match="Error generating embedding: API error"):
        openai_provider.generate_embedding("Valid input")

def test_set_embedding_settings(openai_provider):
    """Test updating embedding model and token limit."""
    openai_provider.set_embedding_settings("new-model", 1024)
    assert openai_provider.model_id == "new-model"
    assert openai_provider.max_input_token == 1024
