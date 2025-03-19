from enum import Enum

class RerankingModelsProvidersEnums(Enum):
    HuggingFaceLocal = 'hugging_face_local'

class HuggingFaceLocalModelIdsEnum(Enum):
    MiniLM_L6_V2_Reranker = 'ms-marco-MiniLM-L6-v2'
    MMACRO_MMINILM_V2_L12 = "mmarco-mMiniLMv2-L12-H384-v1"