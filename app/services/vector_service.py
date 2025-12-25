# -*- coding: utf-8 -*-
"""
向量服务模块

- FAISS 向量存储
- LlamaIndex RAG
- DeepSeek Chat API
"""

import os
from typing import Any, Mapping, List

from openai import OpenAI
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.settings import Settings
from llama_index.core.llms import CustomLLM, CompletionResponse
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
    def metadata(self) -> Mapping[str, Any]:
        return {
            "model": self._model,
            "context_window": 32768,
            "num_output": 4096,
        }

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> str:
        """非流式生成（QueryEngine 实际调用的方法）"""
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": "你是一个专业、可靠的 AI 助手。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        text = resp.choices[0].message.content
        return text

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
    """
    _load_or_create_index()

    if not index.docstore.docs:
        return "错误：向量索引为空，请先上传文档"

    try:
        query_engine = index.as_query_engine(
            similarity_top_k=top_k
        )
        response = query_engine.query(query_text)
        return str(response)
    except Exception as e:
        return f"查询失败：{str(e)}"
