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
from typing import Any, Mapping, List

from openai import OpenAI
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.settings import Settings
from llama_index.core.llms import CustomLLM, CompletionResponse, LLMMetadata
from llama_index.core.llms.callbacks import llm_completion_callback
from llama_index.core.embeddings import MockEmbedding


# =========================
# 配置
# =========================

VECTOR_STORE_PATH = "data/vector_db"
os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

if not DEEPSEEK_API_KEY:
    raise ValueError("请配置 DEEPSEEK_API_KEY 环境变量")


# =========================
# DeepSeek LLM 实现
# =========================

class DeepSeekLLM(CustomLLM):
    """DeepSeek Chat LLM (LlamaIndex CustomLLM 适配)"""

    def __init__(self, api_key: str, base_url: str, model: str):
        # ⚠️ 必须最先调用
        super().__init__()

        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._client = OpenAI(api_key=api_key, base_url=base_url)

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            model_name=self._model,
            context_window=32768,
            num_output=4096,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> str:
        """非流式生成（QueryEngine 实际调用的方法）"""
        try:
            print(f"🔍 DeepSeek API调用 - 提示词长度: {len(prompt)}")
            print(f"🔍 提示词前200字符: {prompt[:200]}...")
            
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "你是一个专业、可靠的 AI 助手。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )

            text = resp.choices[0].message.content
            print(f"✅ DeepSeek API响应成功 - 响应长度: {len(text)}")
            print(f"✅ 响应前200字符: {text[:200]}...")
            return text
        except Exception as e:
            print(f"❌ DeepSeek API调用失败: {str(e)}")
            return f"DeepSeek API调用失败: {str(e)}"

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any):
        """简化处理：先不真正做流式"""
        yield self.complete(prompt, **kwargs)


# =========================
# LlamaIndex 全局设置
# =========================

Settings.llm = DeepSeekLLM(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_API_BASE,
    model=DEEPSEEK_MODEL,
)

# ⚠️ MockEmbedding 只适合 demo / 调试
Settings.embed_model = MockEmbedding(embed_dim=384)

print("✅ DeepSeek LLM 初始化完成（MockEmbedding）")


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
        print("📦 已加载本地向量索引")
    except Exception:
        storage_context = StorageContext.from_defaults()
        index = VectorStoreIndex([], storage_context=storage_context)
        print("🆕 创建新的向量索引")


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
    print(f"✅ 已插入 {len(docs)} 个文档")


def query_vector_store(query_text: str, top_k: int = 5) -> str:
    """
    向量查询接口
    
    问题诊断步骤：
    1. 检查向量索引状态
    2. 检查DeepSeek API调用
    3. 检查查询处理流程
    """
    print(f"🔍 开始查询处理 - 查询内容: {query_text}")
    
    _load_or_create_index()

    # 检查索引中是否有文档
    doc_count = len(index.docstore.docs)
    print(f"📊 向量索引中现有文档数量: {doc_count}")
    
    if doc_count == 0:
        return "错误：向量索引为空，请先上传PDF文档"

    try:
        print(f"🔍 创建查询引擎 - top_k: {top_k}")
        query_engine = index.as_query_engine(
            similarity_top_k=top_k
        )
        
        print(f"🔍 执行查询...")
        response = query_engine.query(query_text)
        
        # 直接获取响应内容 - 使用response.response属性
        if hasattr(response, 'response') and response.response:
            actual_response = response.response
            print(f"✅ 获取到response.response内容")
            print(f"🔍 response.response类型: {type(actual_response)}")
            print(f"🔍 response.response内容长度: {len(str(actual_response))}")
            print(f"🔍 response.response内容: {str(actual_response)[:500]}...")
            
            response_str = str(actual_response)
        else:
            # 如果response.response不存在，尝试其他属性
            print(f"🔍 查询响应类型: {type(response)}")
            print(f"🔍 响应对象属性: {[attr for attr in dir(response) if not attr.startswith('_')]}")
            
            # 尝试直接转换为字符串
            response_str = str(response)
            print(f"🔍 str(response)长度: {len(response_str)}")
            print(f"🔍 str(response)内容: {response_str[:500]}...")
        
        # 检查响应是否为空
        if not response_str or response_str.strip() == "" or response_str.strip() == "Empty Response":
            print("⚠️ 响应为空，尝试使用检索器检查文档匹配情况")
            
            # 使用检索器检查是否找到相关文档
            retriever = index.as_retriever(similarity_top_k=top_k)
            retrieved_nodes = retriever.retrieve(query_text)
            print(f"🔍 检索器找到文档数量: {len(retrieved_nodes)}")
            
            if retrieved_nodes:
                print("✅ 检索器找到了相关文档，但LLM返回空响应")
                # 构建简单的文档摘要
                summary_parts = ["根据检索到的文档，相关内容如下："]
                for i, node in enumerate(retrieved_nodes[:3], 1):
                    preview = node.text[:300] + "..." if len(node.text) > 300 else node.text
                    summary_parts.append(f"\n{i}. {preview}")
                return "\n".join(summary_parts)
            else:
                print("❌ 检索器也未找到相关文档")
                return "抱歉，没有找到相关的文档内容。请尝试用不同的关键词提问。"
        
        return response_str
    except Exception as e:
        print(f"❌ 查询错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"查询失败：{str(e)}"
