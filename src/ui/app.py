import os
import streamlit as st
import requests
import plotly.express as px
import streamlit.components.v1 as components

# Initialize session state
def initialize_state():
    if "file_name" not in st.session_state:
        st.session_state.file_name = None
    if "chunks" not in st.session_state:
        st.session_state.chunks = []
    if "embedding_success" not in st.session_state:
        st.session_state.embedding_success = False
    if "search_results" not in st.session_state:
        st.session_state.search_results = []

# Backend API endpoints
UPLOAD_URL = "http://localhost:8000/api/v1/upload/"
CHUNK_URL = "http://localhost:8000/api/v1/chunk/"
EMBED_URL = "http://localhost:8000/api/v1/embed"
API_URL = "http://localhost:8000/api/v1/retrieve"

st.title("📚 Customizable RAG System")
initialize_state()

# File Upload Section
st.subheader("📤 Upload File")
uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)  # Adds spacing
if st.button("Upload"):
    if uploaded_file:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post(UPLOAD_URL, files=files)
        if response.status_code == 200:
            result = response.json()
            st.session_state.file_name = result.get("file_name")
            st.success(f"✅ Uploaded: {st.session_state.file_name}")
        else:
            st.error("❌ Upload failed.")

# Chunking Options
st.subheader("🔨 Chunking")
col1, col2, col3 = st.columns([1, 1, 1])
chunk_methods = {"Recursive": "recursive", "Sentence": "sentence", "Word": "word"}

with col1:
    chunk_method = st.selectbox("Method", list(chunk_methods.keys()))
with col2:
    chunk_size = st.slider("Size", 50, 1000, 100, 50)
with col3:
    chunk_overlap = st.slider("Overlap", 0, 100, 20, 10, disabled=(chunk_method != "Recursive"))

if st.button("Chunk Text"):
    if st.session_state.file_name:
        params = {
            "file_name": st.session_state.file_name,
            "chunking_method": chunk_methods[chunk_method],
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
        }
        response = requests.get(CHUNK_URL, params=params)
        if response.status_code == 200:
            result = response.json()
            st.session_state.chunks = result.get("sample_chunks", [])[:3]
            st.markdown(f"📄 **Total Chunks:** {result.get('total_chunks')}")
        else:
            st.error("❌ Chunking failed.")

# Display sample chunks
if st.session_state.chunks:
    with st.expander("🔍 View Sample Chunks", expanded=False):
        for i, chunk in enumerate(st.session_state.chunks):
            st.text_area(f"Chunk {i+1}", chunk, height=75)

# Embedding Options
st.subheader("🔗 Embedding")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    provider = st.selectbox("Provider", ["Hugging Face", "OpenAI"])
with col2:
    model_id = st.selectbox("Model ID", ["all-MiniLM-L6-v2", "multi-qa-distilbert-cos-v1"]) if provider == "Hugging Face" else st.text_input("Model ID")
with col3:
    max_input_token = st.number_input("Max Tokens", min_value=1, value=512)

api_key = st.text_input("🔑 API Key", type="password", disabled=(provider == "Hugging Face"))

if st.button("Embed Chunks"):
    if st.session_state.file_name:
        st.session_state.provider = provider
        st.session_state.model_id = model_id
        st.session_state.max_input_token = max_input_token
        st.session_state.api_key = api_key
        payload = {
            "file_name": st.session_state.file_name,
            "provider": provider.lower().replace(" ", "_"),
            "model_id": model_id,
            "max_input_token": max_input_token,
        }
        headers = {"api-key": api_key} if api_key else {}
        response = requests.post(EMBED_URL, json=payload, headers=headers)
        if response.status_code == 200:
            st.session_state.embedding_success = True
            st.success("✅ Chunks embedded successfully!")
        else:
            st.error("❌ Embedding failed.")



st.subheader("📊 Data Visualization")

if "file_name" in st.session_state:
    if st.button("Generate Visualization"):
        visualization_url = f"http://localhost:8000/api/v1/visualize?file_name={st.session_state.file_name}"
        response = requests.get(visualization_url)

        if response.status_code == 200:
            with open("temp_viz.html", "wb") as f:
                f.write(response.content)

            # Display the HTML file
            with open("temp_viz.html", "r", encoding="utf-8") as f:
                html_content = f.read()
                components.html(html_content, height=600, scrolling=True)
        else:
            st.error("❌ Failed to load visualization.")



# Retrieval System
st.subheader("🔍 Search")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    query = st.text_input("Query")
with col2:
    search_technique = st.selectbox("Technique", ["semantic_search", "BM25", "TF-IDF", "ElasticSearch", "Hybrid"])
with col3:
    n_results = st.slider("Results", 1, 10, 3)

if st.button("🔎 Search"):
    if query:
        payload = {
            "file_name": st.session_state.file_name,
            "query": query,
            "search_technique": search_technique,
            "n_results": n_results,
            "provider": st.session_state.provider.lower().replace(" ", "_"),
            "model_id": st.session_state.model_id,
            "max_input_token": st.session_state.max_input_token,
        }
        headers = {"api-key": st.session_state.api_key} if st.session_state.api_key else {}
        print(payload)
        response = requests.post(API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            st.session_state.search_results = response.json().get("results", [])
        else:
            st.error("❌ Retrieval failed.")

# Display search results
if st.session_state.search_results:
    with st.expander("📑 View Search Results", expanded=False):
        for i, result in enumerate(st.session_state.search_results):
            st.write(f"**Result {i+1}:**")
            st.text(result)
