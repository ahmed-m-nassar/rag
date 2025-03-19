from enum import Enum

class OpenAIEnums(Enum):
    SYSTEM_MESSAGE_ROLE = 'system'
    USER_MESSAGE_ROLE = 'user'
    ASSISTANT_MESSAGE_ROLE = 'assistant'

class LLMsProviders(Enum):
    OPENAI = 'openai'
    OLLAMA = 'ollama'