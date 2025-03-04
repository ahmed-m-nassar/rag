from enum import Enum

class ChunkingEnum(str , Enum):
    RECURSIVE = "recursive"
    SENTENCE = "sentence"
    WORD = "word"
    