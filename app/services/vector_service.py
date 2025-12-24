import os
from llama_index import GPTVectorStoreIndex, ServiceContext
from llama_index.vector_stores import FAISSVectorStore
from app.config import VECTOR_STORE_PATH
from llama_index.langchain_helpers.chatgpt import ChatGPTLLMPredictor
from langchain.chat_models import ChatOpenAI

os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

# 初始化 LLM
llm_predictor = ChatGPTLLMPredictor(ChatOpenAI(model_name="kimi-k2-turbo-preview", temperature=0))
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

# 初始化向量数据库
vector_store = FAISSVectorStore.from_documents([], service_context=service_context, persist_path=VECTOR_STORE_PATH)

def add_documents_to_index(docs):
    global vector_store
    vector_store.add_documents(docs)
    vector_store.persist()

def query_vector_store(query_text, top_k=5):
    global vector_store
    response = vector_store.query(query_text, similarity_top_k=top_k, service_context=service_context)
    return response.response
