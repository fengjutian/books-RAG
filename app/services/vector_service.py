import os
from llama_index.core import VectorStoreIndex, ServiceContext, StorageContext
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.llms.openai import OpenAI
from app.config import VECTOR_STORE_PATH

os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

# 初始化 LLM 和服务上下文
llm = OpenAI(model="kimi-k2-turbo-preview", temperature=0)
service_context = ServiceContext.from_defaults(llm=llm)

# 初始化向量数据库
vector_store = FaissVectorStore()
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents([], service_context=service_context, storage_context=storage_context)
index.storage_context.persist(persist_dir=VECTOR_STORE_PATH)

def add_documents_to_index(docs):
    global index
    # 向现有索引添加文档
    for doc in docs:
        index.insert(doc)
    index.storage_context.persist(persist_dir=VECTOR_STORE_PATH)

def query_vector_store(query_text, top_k=5):
    global index
    query_engine = index.as_query_engine(similarity_top_k=top_k)
    response = query_engine.query(query_text)
    return str(response)
