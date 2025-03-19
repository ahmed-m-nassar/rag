from enum import Enum
import textwrap

class LLMEnums(Enum):
    SYSTEM_MESSAGE_ROLE = 'system_message'
    USER_MESSAGE_ROLE = 'user_message'
    ASSISTANT_MESSAGE_ROLE = 'assistant_message'
    SYSTEM_PROMPT = ("You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. "
                     "If you don't know the answer, just say that you don't know. "
                     "Keep your response concise, using a maximum of three sentences. "
                     "Do not provide information beyond what is found in the context.")