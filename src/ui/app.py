import streamlit as st
import requests
import numpy as np
import plotly.express as px

# FastAPI Backend URL
FASTAPI_URL = "http://localhost:8000"

# ------------------------- SIDEBAR -------------------------
st.sidebar.title("🔧 RAG Application Settings")

# File Upload
uploaded_file = st.sidebar.file_uploader("📂 Upload a file", type=["pdf", "txt", "md"])

# Chunking Method
chunking_method = st.sidebar.selectbox(
    "🔍 Choose Chunking Method", ["Fixed Size", "Semantic", "Recursive"]
)

# Embedding Model Selection
embedding_model = st.sidebar.selectbox(
    "🧠 Choose Embedding Model", ["OpenAI", "Cohere", "Hugging Face"]
)

# LLM Model Selection
llm_model = st.sidebar.selectbox(
    "🤖 Choose LLM Model", ["GPT-4 (OpenAI)", "Command R+ (Cohere)"]
)

# Process Button
if st.sidebar.button("🚀 Process File"):
    if uploaded_file:
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(f"{FASTAPI_URL}/upload", files=files)
        if response.status_code == 200:
            st.sidebar.success("✅ File uploaded and processed successfully!")
        else:
            st.sidebar.error("❌ Upload failed.")
    else:
        st.sidebar.warning("⚠ Please upload a file first.")

# ------------------------- MAIN CONTENT -------------------------

st.title("📖 RAG (Retrieval-Augmented Generation) Playground")

# 1️⃣ File Preview & Chunking
st.subheader("📜 File Preview & Chunking")

if uploaded_file:
    file_contents = uploaded_file.getvalue().decode("utf-8")
    st.text_area("File Content", file_contents[:2000], height=200)

    if st.button("🔹 Chunk Document"):
        response = requests.post(
            f"{FASTAPI_URL}/chunk",
            json={"method": chunking_method},
        )
        if response.status_code == 200:
            st.success(f"✅ Document chunked using {chunking_method}")
            chunks = response.json().get("chunks", [])
            for i, chunk in enumerate(chunks[:5]):  # Show first 5 chunks
                st.write(f"🔹 **Chunk {i+1}:** {chunk}")
        else:
            st.error("❌ Chunking failed.")

# 2️⃣ Embedding Visualization
st.subheader("📊 Embedding Visualization")

if st.button("🧠 Generate Embeddings"):
    response = requests.post(
        f"{FASTAPI_URL}/generate-embeddings",
        json={"model": embedding_model},
    )
    if response.status_code == 200:
        st.success(f"✅ Embeddings generated using {embedding_model}")
        
        # Fake embedding data for testing
        embeddings = np.random.rand(10, 3)
        df = {"x": embeddings[:, 0], "y": embeddings[:, 1], "z": embeddings[:, 2]}

        fig = px.scatter_3d(df, x="x", y="y", z="z", title="Embedding Space")
        st.plotly_chart(fig)
    else:
        st.error("❌ Embedding generation failed.")

# 3️⃣ LLM Response Generation
st.subheader("🤖 Ask Your Document")

query = st.text_input("💬 Enter your question:")
if st.button("📝 Generate Response"):
    response = requests.post(
        f"{FASTAPI_URL}/generate-response",
        json={"query": query, "model": llm_model},
    )
    if response.status_code == 200:
        answer = response.json().get("answer", "No response generated.")
        st.write("💬 **User:**", query)
        st.write("🧠 **AI:**", answer)
    else:
        st.error("❌ Response generation failed.")
