import pytest
from unittest.mock import MagicMock, patch
from stores.llm.providers.OpenAILLMProvider import OpenAILLMProvider
from stores.llm.LLMEnum import OpenAIEnums
from models.enums.LLMEnums import LLMEnums
import tiktoken

@pytest.fixture
def llm_provider():
    """Fixture to initialize OpenAILLMProvider with test settings."""
    return OpenAILLMProvider(
        api_key="test-api-key",
        system_prompt="This is a test system prompt.",
        model_id="gpt-4-turbo",
        max_input_tokens=100,
        max_output_tokens=50,
        temperature=0.7,
    )

def test_initialization(llm_provider):
    """Test if the OpenAILLMProvider initializes correctly."""
    assert llm_provider.model_id == "gpt-4-turbo"
    assert llm_provider.max_input_tokens == 100
    assert llm_provider.max_output_tokens == 50
    assert llm_provider.temperature == 0.7
    assert llm_provider.api_key == "test-api-key"
    assert llm_provider.system_prompt == "This is a test system prompt."

def test_validate_token_limit(llm_provider):
    """Test token validation logic."""
    llm_provider.max_input_tokens = 10  # Set a small token limit for testing

    short_message = ["Hello"]
    long_message = ["This is a long message exceeding the token limit."] * 10
    
    # Mock token encoding
    with patch("tiktoken.encoding_for_model") as mock_encoding:
        mock_encoding.return_value.encode.side_effect = lambda x: x.split()
        
        # Short message should pass
        llm_provider.validate_token_limit(short_message)

        # Long message should raise an exception
        with pytest.raises(ValueError, match="Total input tokens .* exceed the max limit"):
            llm_provider.validate_token_limit(long_message)

@patch("stores.llm.providers.OpenAILLMProvider.OpenAI")
def test_generate_response(mock_openai, llm_provider):
    """Test generate_response method with a mocked OpenAI API response."""
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message={"content": "Test response"})])

    result = llm_provider.generate_response("Hello!")
    
    assert result == "Test response"
    mock_client.chat.completions.create.assert_called_once()

@patch("stores.llm.providers.OpenAILLMProvider.OpenAI")
def test_generate_chat_history_response(mock_openai, llm_provider):
    """Test generate_chat_history_response with a mocked OpenAI API response."""
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message={"content": "Chat response"})])

    chat_history = [
        {"role": OpenAIEnums.USER_MESSAGE_ROLE.value, "content": "Hi!"},
        {"role": OpenAIEnums.ASSISTANT_MESSAGE_ROLE.value, "content": "Hello!"}
    ]

    result = llm_provider.generate_chat_history_response(chat_history)
    
    assert result == "Chat response"
    mock_client.chat.completions.create.assert_called_once()

def test_construct_chat_history(llm_provider):
    """Test if construct_chat_history correctly formats messages."""
    chat_messages = [
        {"role": LLMEnums.USER_MESSAGE_ROLE.value, "content": "User message"},
        {"role": LLMEnums.ASSISTANT_MESSAGE_ROLE.value, "content": "Assistant message"},
        {"role": LLMEnums.SYSTEM_MESSAGE_ROLE.value, "content": "System message"},
    ]
    
    formatted_messages = llm_provider.construct_chat_history(chat_messages)
    
    assert formatted_messages == [
        {"role": OpenAIEnums.USER_MESSAGE_ROLE.value, "content": "User message"},
        {"role": OpenAIEnums.ASSISTANT_MESSAGE_ROLE.value, "content": "Assistant message"},
        {"role": OpenAIEnums.SYSTEM_MESSAGE_ROLE.value, "content": "System message"},
    ]