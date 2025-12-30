# -*- coding: utf-8 -*-
# =========================
# DeepSeek LLM 实现
# =========================

import logging
from typing import Any
from openai import OpenAI
from llama_index.core.llms import CustomLLM, CompletionResponse, LLMMetadata
from llama_index.core.llms.callbacks import llm_completion_callback

logger = logging.getLogger(__name__)

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
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """非流式生成（QueryEngine 实际调用的方法）"""
        try:
            logger.info("DeepSeek API调用 - 提示词长度: %d", len(prompt))
            logger.debug("DeepSeek API调用 - 提示词前200字符: %s", prompt[:200] + "...")
            
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "你是一个专业、可靠的 AI 助手。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )

            text = resp.choices[0].message.content
            logger.info("DeepSeek API响应成功 - 响应长度: %d", len(text))
            logger.debug("DeepSeek API响应成功 - 响应前200字符: %s", text[:200] + "...")
            return CompletionResponse(text=text)
        except Exception as e:
            logger.error("DeepSeek API调用失败: %s", str(e))
            return CompletionResponse(text=f"DeepSeek API调用失败: {str(e)}")

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any):
        """简化处理：先不真正做流式"""
        response = self.complete(prompt, **kwargs)
        yield response
