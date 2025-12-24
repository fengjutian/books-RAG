# -*- coding: utf-8 -*-
"""
向量服务模块

该模块负责向量存储的初始化、文档索引管理和向量查询功能。
使用FAISS作为向量数据库，结合LlamaIndex框架提供RAG功能支持。
"""

import os
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings
from llama_index.embeddings.openai import OpenAIEmbedding

# ------------------------------ 配置部分 ------------------------------
# 向量存储持久化路径
VECTOR_STORE_PATH = "data/vector_db"
# 创建向量存储目录（如果不存在）
os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

# ------------------------------ 模型初始化 ------------------------------
# 设置全局语言模型
# 使用OpenAI兼容的kimi-k2-turbo-preview模型，温度参数设为0以获得更确定性的输出
Settings.llm = OpenAI(model="kimi-k2-turbo-preview", temperature=0)

# 设置全局嵌入模型
# 使用OpenAI嵌入模型
Settings.embed_model = OpenAIEmbedding()

# ------------------------------ 向量存储初始化 ------------------------------
# 延迟初始化索引对象
index = None
storage_context = None

# ------------------------------ 功能函数 ------------------------------

def add_documents_to_index(docs):
    """
    向现有向量索引中添加文档
    
    参数:
        docs (list): 要添加的文档列表，每个文档应为LlamaIndex的Document对象
        
    返回值:
        None
    """
    global index, storage_context
    
    # 如果索引不存在，先初始化
    if index is None:
        try:
            # 尝试从持久化目录加载现有索引
            storage_context = StorageContext.from_defaults(persist_dir=VECTOR_STORE_PATH)
            index = VectorStoreIndex.from_documents([], storage_context=storage_context)
        except:
            # 如果加载失败，创建新的索引
            storage_context = StorageContext.from_defaults()
            index = VectorStoreIndex([], storage_context=storage_context)
    
    # 遍历文档列表，逐个插入到索引中
    for doc in docs:
        index.insert(doc)
    
    # 将更新后的索引持久化到本地
    index.storage_context.persist(persist_dir=VECTOR_STORE_PATH)


def query_vector_store(query_text, top_k=5):
    """
    在向量存储中查询相关文档并返回结果
    
    参数:
        query_text (str): 查询文本
        top_k (int, optional): 返回最相关的文档数量，默认值为5
        
    返回值:
        str: 查询结果的文本表示
    """
    global index, storage_context
    
    # 如果索引不存在，先尝试加载
    if index is None:
        try:
            # 尝试从持久化目录加载现有索引
            storage_context = StorageContext.from_defaults(persist_dir=VECTOR_STORE_PATH)
            index = VectorStoreIndex.from_documents([], storage_context=storage_context)
            
            # 检查索引中是否有文档
            if len(index.docstore.docs) == 0:
                return "错误：向量索引为空，请先上传PDF文件"
                
        except Exception as e:
            print(f"Error loading index: {e}")
            # 如果加载失败，返回错误信息
            return "错误：无法加载向量索引，请先上传PDF文件"
    
    # 检查索引中是否有文档
    if len(index.docstore.docs) == 0:
        return "错误：向量索引为空，请先上传PDF文件"
    
    try:
        # 将索引转换为查询引擎，设置返回结果的数量
        query_engine = index.as_query_engine(similarity_top_k=top_k)
        # 执行查询
        response = query_engine.query(query_text)
        # 返回查询结果的字符串表示
        return str(response)
    except Exception as e:
        print(f"Query error: {e}")
        return f"查询失败：{str(e)}"
