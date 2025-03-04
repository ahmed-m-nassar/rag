import os
from openai import OpenAI
from typing import List, Dict, Any
from stores.llm.LLMInterface import LLMInterface
from models.enums.LLMEnums import LLMEnums
from stores.llm.LLMEnum import OpenAIEnums
import tiktoken

class OpenAILLMProvider(LLMInterface):
    """Implementation of LLMInterface using OpenAI API."""

    def __init__(self,
                api_key: str, 
                system_prompt : str = None,
                model_id: str = "gpt-4-turbo",  
                max_input_tokens: int = 4096,   
                max_output_tokens: int = 512,   
                temperature: float = 0.1,
                ):      

        self.model_id = model_id
        self.max_input_tokens = max_input_tokens
        self.max_output_tokens = max_output_tokens
        self.temperature = temperature
        self.api_key = api_key
        self.system_prompt = system_prompt

        self.client = OpenAI(api_key=self.api_key)

    def generate_response(self, prompt: str) -> str:
        messages = []
        if self.system_prompt:
            messages.append({"role": OpenAIEnums.SYSTEM_MESSAGE_ROLE.value, "content": self.system_prompt})
        
        messages.append({"role": OpenAIEnums.USER_MESSAGE_ROLE.value, "content": prompt})
        
        self.validate_token_limit([message["content"] for message in messages])

        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            max_completion_tokens=self.max_output_tokens,
            temperature = self.temperature
        )
        return response.choices[0].message["content"].strip()

    def generate_chat_history_response(
        self, chat_history: List[Dict[str, str]] ) -> str:

        messages = self.construct_chat_history(chat_history)

        self.validate_token_limit([message["content"] for message in messages])

        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            max_completion_tokens=self.max_output_tokens,
            temperature = self.temperature )
        
        return response.choices[0].message["content"].strip()

    def validate_token_limit(self, messages: List[str]):
        """
        Validates that the total token count in chat history does not exceed the max_input_tokens.
        
        :param messages: List of chat messages.
        :raises ValueError: If the token count exceeds the allowed limit.
        """
        encoding = tiktoken.encoding_for_model(self.model_id)  # Get token encoder

        total_tokens = sum(len(encoding.encode(message)) for message in messages)

        if total_tokens > self.max_input_tokens:
            raise ValueError(f"Total input tokens ({total_tokens}) exceed the max limit ({self.max_input_tokens}).")

    def construct_chat_history(self , messages : List[Dict[str, str]]) : 
        constructed_messages = []
        for message in messages :
            if message.role == LLMEnums.SYSTEM_MESSAGE_ROLE.value :
                constructed_messages.append({
                                            "role": OpenAIEnums.SYSTEM_MESSAGE_ROLE.value,
                                            "content": message.content
                                        })
                
            elif message.role == LLMEnums.ASSISTANT_MESSAGE_ROLE.value : 
                constructed_messages.append({
                                            "role": OpenAIEnums.ASSISTANT_MESSAGE_ROLE.value,
                                            "content": message.content
                                        })
                
            elif message.role == LLMEnums.USER_MESSAGE_ROLE.value : 
                constructed_messages.append({
                                            "role": OpenAIEnums.USER_MESSAGE_ROLE.value,
                                            "content": message.content
                                        })
            else:
                raise ValueError(f"Invalid message role: {message.role}")

        return constructed_messages
                

    def set_model_parameters(self, **kwargs: Any):
        for key, value in kwargs.items():
            setattr(self, key, value)
