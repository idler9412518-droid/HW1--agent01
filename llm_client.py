# llm_client.py
import os
import time
import random
from typing import Any

from openai import OpenAI, APIStatusError, APITimeoutError, APIConnectionError


class LLMClient:
    """封装千问 OpenAI 兼容接口，带指数退避重试。"""

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url=os.getenv(
                "DASHSCOPE_BASE_URL",
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
            ),
        )
        self.model = os.getenv("QWEN_MODEL", "qwen-plus")

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        max_retries: int = 3,
    ) -> Any:
        """调用 chat.completions，对 429/5xx/超时做指数退避重试。"""
        last_error = None
        for attempt in range(max_retries):
            try:
                kwargs: dict[str, Any] = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.1,
                }
                if tools:
                    kwargs["tools"] = tools

                return self.client.chat.completions.create(**kwargs)

            except APIStatusError as e:
                last_error = e
                # 429 限流、5xx 服务端错误：可重试
                if e.status_code == 429 or e.status_code >= 500:
                    wait = min(2 ** attempt + random.uniform(0, 0.5), 10)
                    print(f"[LLM] 可重试错误 {e.status_code}，{wait:.1f}s 后重试...")
                    time.sleep(wait)
                    continue
                raise  # 401/404 等不可重试错误，直接抛出

            except (APITimeoutError, APIConnectionError) as e:
                last_error = e
                wait = min(2 ** attempt + random.uniform(0, 0.5), 10)
                print(f"[LLM] 网络/超时错误，{wait:.1f}s 后重试...")
                time.sleep(wait)

        raise RuntimeError(f"LLM 调用重试 {max_retries} 次仍失败: {last_error}")