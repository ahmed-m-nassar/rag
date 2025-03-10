from fastapi import APIRouter,Request
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
import logging
import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.manifold import TSNE
from helpers.config import get_settings
import os
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

visualize_router = APIRouter(
    prefix="/api/v1/visualize",
    tags=["api_v1", "visualize"],
)
def save_interactive_embeddings(vectors, file_directory, file_name, labels=None, perplexity=5):
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

@visualize_router.get("/")
async def get_visualizations(request : Request , 
                             file_name : str):

    settings = get_settings()

    data = request.app.vectordb.get_collection(os.path.splitext(file_name)[0]).get(include=['embeddings', 'documents'] )
    chunks = data.get("documents", [])
    embeddings = data.get("embeddings", [])

    visualization_file_path = save_interactive_embeddings(embeddings, perplexity=5 , labels=chunks , file_directory=settings.VISUALIZATIONS_DIR , file_name=os.path.splitext(file_name)[0] + "_viz.html")

    return FileResponse(
        visualization_file_path, 
        media_type="text/html", 
        filename=os.path.basename(visualization_file_path)
    )
