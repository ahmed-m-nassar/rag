from  stores.reranking.RerankingInterface import RerankingInterface
from  stores.reranking.RerankingEnum import RerankingModelsProvidersEnums , HuggingFaceLocalModelIdsEnum
from stores.reranking.providers.HuggingFaceRerankerProvider import HuggingFaceRerankerProvider
class RerankerProviderFactory:
    """Factory to create reranking model instances."""

    @staticmethod
    def get_reranker(provider: RerankingModelsProvidersEnums , model_id : str , api_key : str = None) -> RerankingInterface:
        """Returns the appropriate reranker instance."""
        if provider == RerankingModelsProvidersEnums.HuggingFaceLocal:
            return HuggingFaceRerankerProvider(model_id=HuggingFaceLocalModelIdsEnum(model_id))
        return None
        #return RerankerFactory.RERANKERS[model_type.lower()]()