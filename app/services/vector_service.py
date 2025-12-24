# vector_service.py

import os
import faiss
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Configuration
VECTOR_STORE_PATH = "data/vector_db"
os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

# Initialize LLM and settings
Settings.llm = OpenAI(model="kimi-k2-turbo-preview", temperature=0)
# Use local embedding model to avoid needing OpenAI API key
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize vector store with empty FAISS index
# Create a simple FAISS index with 384 dimensions (default for sentence-transformers/all-MiniLM-L6-v2)
faiss_index = faiss.IndexFlatL2(384)
vector_store = FaissVectorStore(faiss_index=faiss_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents([], storage_context=storage_context)
index.storage_context.persist(persist_dir=VECTOR_STORE_PATH)

def add_documents_to_index(docs):
    global index
    # Add documents to existing index
    for doc in docs:
        index.insert(doc)
    index.storage_context.persist(persist_dir=VECTOR_STORE_PATH)

def query_vector_store(query_text, top_k=5):
    global index
    query_engine = index.as_query_engine(similarity_top_k=top_k)
    response = query_engine.query(query_text)
    return str(response)
