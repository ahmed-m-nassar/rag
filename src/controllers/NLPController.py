import os
import json
import logging
import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.manifold import TSNE
from .BaseController import BaseController
from stores.vectordb.VectorDBInterface import VectorDBInterface
from stores.embedding.EmbeddingInterface import EmbeddingInterface
from stores.reranking.RerankingInterface import RerankingInterface
from stores.llm.LLMInterface import LLMInterface
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLPController(BaseController):
    
    def __init__(self):
        super().__init__()

    async def create_interactive_embeddings(self , vectors, file_directory, file_name, labels=None, perplexity=5):
        """
        Plots an interactive 2D visualization of embeddings using t-SNE and saves it as an HTML file.
        Labels will only be shown when hovering over a point.

        Parameters:
        - vectors (list or np.array): A list/array of embedding vectors.
        - file_directory (str): Directory to save the visualization file.
        - file_name (str): Name of the saved HTML file.
        - labels (list of str, optional): A list of text chunks corresponding to each embedding.
        - perplexity (int, optional): Perplexity for t-SNE (recommended between 5-50). Default is 5.

        Returns:
        - str: The path to the saved HTML file.
        """
        vectors = np.array(vectors)  # Ensure input is a NumPy array
        n_samples = len(vectors)  # Get the number of vectors

        # Adjust perplexity to be within the valid range
        perplexity = min(perplexity, max(1, n_samples - 1))

        # Apply t-SNE for dimensionality reduction
        tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42)
        reduced_vectors = tsne.fit_transform(vectors)

        # Create a DataFrame for visualization
        df = pd.DataFrame(reduced_vectors, columns=["x", "y"])

        # Ensure labels are a list of texts, otherwise set them to None
        if labels is not None and isinstance(labels, list) and len(labels) == n_samples:
            df["label"] = labels
        else:
            df["label"] = [None] * n_samples  # Empty tooltips if no valid labels

        # Create an interactive scatter plot with hover text
        fig = px.scatter(
            df, x="x", y="y", hover_data={"label": True},  # Show labels only on hover
            title="Interactive t-SNE Visualization of Embeddings",
            labels={"x": "t-SNE Component 1", "y": "t-SNE Component 2"}
        )

        fig.update_traces(marker=dict(size=10, opacity=0.7))

        # Ensure directory exists before saving
        os.makedirs(file_directory, exist_ok=True)

        # Save the plot as an interactive HTML file
        saved_file_path = os.path.join(file_directory, file_name)
        fig.write_html(saved_file_path)

        return saved_file_path
    
    async def semantic_search(self , 
                              vectordb : VectorDBInterface ,
                              embedding_client :EmbeddingInterface,
                              collection_name : str ,
                              query : str ,
                              n_results : str ):
        embeddings = embedding_client.generate_embedding(texts=[query])
        return vectordb.query_embeddings(collection_name=collection_name ,
                                         n_results=n_results , 
                                         embeddings=embeddings ).get('documents', [])[0]

    async def rerank(self , 
                    reranking_client :RerankingInterface,
                    query : str ,
                    docs : list ):
        results = reranking_client.rerank(query=query , documents=docs)
        return results
    
    async def generate_response(self , 
                llm_client :LLMInterface,
                query : str  ):
        
        return llm_client.generate_response(prompt=query )
        
    
    async def create_generation_query(self , 
                                      question : str , 
                                      docs : list):
        context = "\n".join(docs) if docs else "No relevant context available."

        # Format the query string
        query = f"Question: {question}\nContext: {context}\nAnswer:"
        
        return query
                