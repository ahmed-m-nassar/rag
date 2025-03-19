from  stores.reranking.RerankingInterface import RerankingInterface
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from stores.reranking.RerankingEnum import HuggingFaceLocalModelIdsEnum
from helpers.config import get_settings
import torch
import os

class HuggingFaceRerankerProvider(RerankingInterface):
    def __init__(self, model_id: HuggingFaceLocalModelIdsEnum):
        """
        Initialize the reranker with a locally saved model.

        :param local_model_path: The path to the locally saved Hugging Face model and tokenizer.
        """
        settings = get_settings()
        model_path = os.path.join(settings.RERANKING_MODELS_DIR, model_id.value)
        if not os.path.exists(model_path):
            raise ValueError(f"Model path '{model_path}' does not exist!")

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.eval()  # Set model to evaluation mode

    def rerank(self, query: str, documents: list) -> list:
        """
        Rerank the given documents based on relevance to the query.

        :param query: The input query string.
        :param documents: A list of document strings.
        :return: A list of (document, score), sorted by relevance.
        """
        scores = []
        for doc in documents:
            inputs = self.tokenizer(query, doc, return_tensors="pt", truncation=True, padding=True)
            with torch.no_grad():
                score = self.model(**inputs).logits.squeeze().item()
            scores.append((doc, score))
        
        return sorted(scores, key=lambda x: x[1], reverse=True)