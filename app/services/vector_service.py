# vector_service.py

from llama_index.indices.vector_store.vector_store import VectorStoreIndex

from llama_index.vector_stores import FAISSVectorStore
from llama_index.settings import Settings
from llama_index.langchain_helpers.chatgpt import ChatGPTLLMPredictor
from langchain.chat_models import ChatOpenAI

# LLM 初始化
llm_predictor = ChatGPTLLMPredictor(ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0))
settings = Settings(llm_predictor=llm_predictor)

# 初始化向量存储
vector_store = FAISSVectorStore.from_documents([], persist_path="data/vector_db")

def add_documents_to_index(docs):
    index = VectorStoreIndex.from_documents(docs, vector_store=vector_store, settings=settings)
    vector_store.persist()

def query_vector_store(query_text, top_k=5):
    response = vector_store.query(query_text, similarity_top_k=top_k, settings=settings)
    return response.response
