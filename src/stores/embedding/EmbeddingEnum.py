from enum import Enum

class EmbeddingEnum(str, Enum):
    OPENAI = "openai"
    HUGGINGFACE = "hugging_face"

class HuggingFaceLocalModels(str , Enum) :
    ALL_MINILM_L6_V2 = "all-MiniLM-L6-v2"
    MULTI_QA_DISTILBERT_COS_V1 = "multi-qa-distilbert-cos-v1"