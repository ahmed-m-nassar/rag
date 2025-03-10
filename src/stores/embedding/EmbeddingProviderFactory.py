
from .EmbeddingEnum import EmbeddingEnum
from .providers.OpenAIEmbeddingProvider import OpenAIEmbeddingProvider
from .providers.HuggingFaceLocalEmbeddingProvider import HuggingFaceLocalEmbeddingProvider

class EmbeddingProviderFactory:
    def __init__(self,  
                 api_key,
                 model_id,
                 max_input_token):
        self.api_key = api_key
        self.model_id = model_id
        self.max_input_token = max_input_token

    def create(self, provider: str):
        if provider == EmbeddingEnum.OPENAI.value:
            return OpenAIEmbeddingProvider(
                api_key = self.api_key,
                model_id = self.model_id,
                max_input_token=self.max_input_token,
            )

        if provider == EmbeddingEnum.HUGGINGFACE.value:
            return HuggingFaceLocalEmbeddingProvider(
                model_id = self.model_id,
                max_input_token=self.max_input_token,
            )

        return None