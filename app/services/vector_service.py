# -*- coding: utf-8 -*-
"""
向量服务模块

- FAISS 向量存储
- LlamaIndex RAG
- DeepSeek Chat API

问题诊断：
1. 文档插入成功（680个向量）
2. 查询返回空，可能原因：
   - DeepSeek API调用失败
   - 查询处理逻辑问题
   - 向量索引构建问题
"""

import os
import logging
from typing import Any, Mapping, List

from app.logger.logging_config import get_logging_config
from app.config import config

from openai import OpenAI
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.settings import Settings
from llama_index.core.llms import CustomLLM, CompletionResponse, LLMMetadata
from llama_index.core.llms.callbacks import llm_completion_callback
from llama_index.core.embeddings import MockEmbedding

# 导入PyTorch用于CUDA检测
import torch

# 导入HuggingFace嵌入模型
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.llm.DeepSeekLLM import DeepSeekLLM

# 配置日志
logging.config.dictConfig(get_logging_config(config.DEBUG))
logger = logging.getLogger("app")


# =========================
# 配置
# =========================

# 从配置对象获取配置
VECTOR_STORE_PATH = config.VECTOR_STORE_PATH
os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

DEEPSEEK_API_KEY = config.DEEPSEEK_API_KEY
DEEPSEEK_API_BASE = config.DEEPSEEK_API_BASE
DEEPSEEK_MODEL = config.DEEPSEEK_MODEL


# =========================
# LlamaIndex 全局设置
# =========================

Settings.llm = DeepSeekLLM(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_API_BASE,
    model=DEEPSEEK_MODEL,
)

# ⚠️ MockEmbedding 只适合 demo / 调试
# Settings.embed_model = MockEmbedding(embed_dim=384)

# logger.info("DeepSeek LLM 初始化完成（使用 MockEmbedding）")

# 检测CUDA是否可用
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info("使用设备进行嵌入计算: %s", device)

# 使用真实的HuggingFace嵌入模型
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",  # 指定模型名称
    embed_batch_size=100,  # 可根据需要调整批量大小
    device=device  # 动态设置设备
)


# =========================
# 向量索引（延迟初始化）
# =========================

index: VectorStoreIndex | None = None
storage_context: StorageContext | None = None


# =========================
# 对外函数
# =========================

def _load_or_create_index():
    global index, storage_context

    if index is not None:
        return

    try:
        storage_context = StorageContext.from_defaults(
            persist_dir=VECTOR_STORE_PATH
        )
        index = VectorStoreIndex.from_documents(
            [],
            storage_context=storage_context,
        )
        logger.info("已加载本地向量索引")
    except Exception:
        storage_context = StorageContext.from_defaults()
        index = VectorStoreIndex([], storage_context=storage_context)
        logger.info("创建新的向量索引")


def add_documents_to_index(docs: List):
    """
    添加文档到向量索引
    docs: List[llama_index.core.schema.Document]
    """
    _load_or_create_index()

    if not docs:
        return

    for doc in docs:
        index.insert(doc)

    index.storage_context.persist(persist_dir=VECTOR_STORE_PATH)
    logger.info("已插入 %d 个文档到向量索引", len(docs))


def query_vector_store(query_text: str, top_k: int = 5) -> str:
    """
    向量查询接口
    
    问题诊断步骤：
    1. 检查向量索引状态
    2. 检查DeepSeek API调用
    3. 检查查询处理流程
    """
    logger.info("开始查询处理 - 查询内容: %s", query_text)
    
    _load_or_create_index()

    # 检查索引中是否有文档
    doc_count = len(index.docstore.docs)
    logger.info("向量索引中现有文档数量: %d", doc_count)
    
    if doc_count == 0:
        return "错误：向量索引为空，请先上传PDF文档"

    try:
        logger.info("创建查询引擎 - top_k: %d", top_k)
        query_engine = index.as_query_engine(
            similarity_top_k=top_k
        )
        
        logger.info("执行查询...")
        response = query_engine.query(query_text)
        
        # 详细检查响应对象
        logger.debug("查询响应类型: %s", type(response))
        logger.debug("响应对象属性: %s", [attr for attr in dir(response) if not attr.startswith('_')])
        
        # 尝试多种方式获取响应内容
        response_str = ""
        
        # 方法1: 检查response属性
        if hasattr(response, 'response') and response.response:
            actual_response = response.response
            logger.info("获取到response.response内容")
            logger.debug("response.response类型: %s", type(actual_response))
            logger.debug("response.response内容长度: %d", len(str(actual_response)))
            logger.debug("response.response内容: %s", str(actual_response)[:500] + "...")
            response_str = str(actual_response)
        
        # 方法2: 检查其他可能的属性
        elif hasattr(response, 'response_txt') and response.response_txt:
            response_str = response.response_txt
            logger.info("使用response_txt属性获取响应内容")
        
        # 方法3: 检查是否有get_response()方法
        elif hasattr(response, 'get_response') and callable(getattr(response, 'get_response')):
            response_str = response.get_response()
            logger.info("使用get_response()方法获取响应内容")
        
        # 方法4: 直接转换为字符串
        else:
            response_str = str(response)
            logger.info("直接转换response对象为字符串")
            logger.debug("转换后的响应长度: %d", len(response_str))
            logger.debug("转换后的响应内容: %s", response_str[:500] + "...")
        
        # 检查响应是否为空
        if not response_str or response_str.strip() == "" or response_str.strip() == "Empty Response":
            logger.warning("响应为空，尝试手动构建查询流程")
            
            # 手动构建查询流程：检索 + 手动调用LLM
            retriever = index.as_retriever(similarity_top_k=top_k)
            retrieved_nodes = retriever.retrieve(query_text)
            logger.info("检索器找到文档数量: %d", len(retrieved_nodes))
            
            if retrieved_nodes:
                logger.info("检索器找到了相关文档，手动构建提示词")
                
                # 构建上下文
                context_parts = ["根据以下文档内容回答问题："]
                for i, node in enumerate(retrieved_nodes, 1):
                    context_parts.append(f"\n--- 文档 {i} ---")
                    context_parts.append(node.text[:1000])  # 限制每个文档长度
                
                context_text = "\n".join(context_parts)
                full_prompt = f"{context_text}\n\n问题：{query_text}"
                
                # 直接调用LLM，但需要包装成CompletionResponse
                from app.services.vector_service import Settings
                from llama_index.core.llms import CompletionResponse
                
                raw_response = Settings.llm.complete(full_prompt)
                
                # 检查是否是CompletionResponse对象
                if isinstance(raw_response, CompletionResponse):
                    llm_response = raw_response.text
                else:
                    llm_response = str(raw_response)
                
                if llm_response and not llm_response.startswith("DeepSeek API调用失败"):
                    logger.info("手动LLM调用成功")
                    return llm_response
                else:
                    # 如果LLM调用失败，返回文档摘要
                    logger.warning("手动LLM调用失败，返回文档摘要")
                    summary_parts = ["根据检索到的文档，相关内容如下："]
                    for i, node in enumerate(retrieved_nodes[:3], 1):
                        preview = node.text[:300] + "..." if len(node.text) > 300 else node.text
                        summary_parts.append(f"\n{i}. {preview}")
                    return "\n".join(summary_parts)
            else:
                logger.warning("检索器也未找到相关文档")
                return "抱歉，没有找到相关的文档内容。请尝试用不同的关键词提问。"
        
        return response_str
    except Exception as e:
        logger.error("查询错误: %s", str(e), exc_info=True)
        return f"查询失败：{str(e)}"
