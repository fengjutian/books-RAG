# -*- coding: utf-8 -*-
"""
向量服务模块

该模块负责向量存储的初始化、文档索引管理和向量查询功能。
使用FAISS作为向量数据库，结合LlamaIndex框架提供RAG功能支持。
使用Kimi API作为语言模型。
"""

import os
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.settings import Settings
from openai import OpenAI

# ------------------------------ 配置部分 ------------------------------
# 向量存储持久化路径
VECTOR_STORE_PATH = "data/vector_db"
# 创建向量存储目录（如果不存在）
os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

# ------------------------------ 模型初始化 ------------------------------
# 检查DeepSeek API密钥配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
    raise ValueError("请配置有效的DeepSeek API密钥。请编辑.env文件并设置DEEPSEEK_API_KEY")

# 初始化DeepSeek客户端
deepseek_client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_API_BASE,
)

# 设置全局语言模型 - 使用自定义的DeepSeek LLM包装器
from llama_index.core.llms import CustomLLM
from llama_index.core.llms.callbacks import llm_completion_callback
from typing import Optional, List, Mapping, Any

class DeepSeekLLM(CustomLLM):
    """DeepSeek语言模型包装器"""
    
    def __init__(self, client, model="deepseek-chat"):
        self.client = client
        self.model = model
        super().__init__()
    
    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> str:
        """完成文本生成"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个有用的AI助手，擅长中文和英文对话。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"DeepSeek API调用失败: {str(e)}"
    
    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any) -> str:
        """流式完成（暂不支持）"""
        return self.complete(prompt, **kwargs)
    
    @property
    def metadata(self) -> Mapping[str, Any]:
        """模型元数据"""
        return {
            "model": self.model,
            "context_window": 32768,
            "num_output": 4096,
        }

# 设置全局语言模型
Settings.llm = DeepSeekLLM(deepseek_client, DEEPSEEK_MODEL)

# 设置全局嵌入模型 - 使用本地嵌入模型避免API调用
from llama_index.core.embeddings import MockEmbedding
Settings.embed_model = MockEmbedding(embed_dim=384)
print("✅ 使用Kimi API作为语言模型，本地嵌入模型")

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
