from stores.llm.LLMEnum import OpenAIEnums
from stores.llm.LLMEnum import LLMsProviders
from stores.llm.LLMInterface import LLMInterface
from stores.llm.providers.OllamaLLMProvider import OllamaLLMProvider
class LLMProviderFactory:
    """Factory to create reranking model instances."""

    @staticmethod
    def get_llm(provider: LLMsProviders ,
                model_id : str ,
                system_prompt : str = None , 
                base_url :str = None,
                api_key : str = None) -> LLMInterface:
        """Returns the appropriate llm instance."""
        if provider == LLMsProviders.OLLAMA:
            return OllamaLLMProvider(model= model_id ,
                                     base_url=base_url,
                                     system_prompt=system_prompt,
                                     )
        return None
        #return RerankerFactory.RERANKERS[model_type.lower()]()