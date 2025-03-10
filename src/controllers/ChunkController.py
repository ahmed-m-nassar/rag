import os
import json
import logging
from .BaseController import BaseController
from langchain_text_splitters import RecursiveCharacterTextSplitter
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from models.enums.ChunkingEnum import ChunkingEnum
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChunkController(BaseController):
    
    def __init__(self):
        super().__init__()
        nltk.download('punkt_tab')


    async def save_chunks(self, chunks: list[str], file_directory: str , file_name : str):
        """
        Saves the chunked text into a JSON file for later retrieval.

        Args:
            chunks (list[str]): List of chunked text segments.
            file_directory (str): Directory where the file will be saved.
            file_name (str): Original file name to create a chunk file.
        """
        # Ensure the directory exists
        os.makedirs(file_directory, exist_ok=True)

        # Define the file path (store as a JSON file)
        chunk_file_path = os.path.join(file_directory, file_name)

        # Save chunks as a JSON file
        with open(chunk_file_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=4)

        return True
        
    async def load_chunks(self, file_directory: str , file_name : str) -> list[str]:
        """
        Loads chunked text from a previously saved JSON file.

        Args:
            file_directory (str): Directory where the chunk file is stored.
            file_name (str): Original file name to retrieve its chunks.

        Returns:
            list[str]: List of chunked text segments.
        """
        # Define the file path
        chunk_file_path = os.path.join(file_directory, file_name)
        print(chunk_file_path)
        # Check if the file exists
        if not os.path.exists(chunk_file_path):
            return {"status": "error", "message": "Chunk file chunks.json not found"}

        # Load chunks from JSON file
        with open(chunk_file_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        return chunks  # Returning list of strings

    async def chunk_text(
        self, 
        text: str, 
        chunk_size: int = 100, 
        chunk_overlap: int = 20, 
        method: str = "recursive"
    ):
        """
        Main function to chunk text using different methods.

        Args:
            text (str): The input text to be chunked.
            chunk_size (int): Size of each chunk.
            chunk_overlap (int): Overlap between chunks (for applicable methods).
            method (str): Chunking method ('recursive', 'fixed', 'sentence', 'word').

        Returns:
            list: List of chunked text segments.
        """
        if method == ChunkingEnum.RECURSIVE.value:
            return self.__recursive_chunking(text, chunk_size, chunk_overlap)
        elif method == ChunkingEnum.SENTENCE.value:
            return self.__sentence_chunking(text, chunk_size)
        elif method == ChunkingEnum.WORD.value:
            return self.__word_chunking(text, chunk_size)
        else:
            raise ValueError(f"Invalid chunking method '{method}'. Choose from ['recursive', 'fixed', 'sentence', 'word'].")



    def __recursive_chunking(self, text: str, chunk_size: int, chunk_overlap: int):
        """
        Chunks text using RecursiveCharacterTextSplitter from LangChain.

        Args:
            text (str): Input text.
            chunk_size (int): Desired chunk size.
            chunk_overlap (int): Overlap between chunks.

        Returns:
            list: List of chunked text segments.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        documents = text_splitter.create_documents([text])
        chunked_texts = [doc.page_content for doc in documents]
        return chunked_texts

    def __sentence_chunking(self, text: str, chunk_size: int):
        """
        Splits text into sentences and groups them into chunks of specified size.

        Args:
            text (str): Input text.
            chunk_size (int): Desired chunk size in characters.

        Returns:
            list: List of chunked text segments.
        """
        sentences = sent_tokenize(text)
        chunks = []
        temp_chunk = []
        char_count = 0

        for sentence in sentences:
            temp_chunk.append(sentence)
            char_count += len(sentence)
            if char_count >= chunk_size:
                chunks.append(" ".join(temp_chunk))
                temp_chunk = []
                char_count = 0
        
        if temp_chunk:
            chunks.append(" ".join(temp_chunk))

        return chunks

    def __word_chunking(self, text: str, chunk_size: int):
        """
        Splits text into word-based chunks.

        Args:
            text (str): Input text.
            chunk_size (int): Desired number of words per chunk.

        Returns:
            list: List of chunked text segments.
        """
        words = word_tokenize(text)
        return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]