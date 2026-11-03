# agent.py
import json
from typing import Any

from llm_client import LLMClient
from prompts import SYSTEM_PROMPT
from tools import TOOL_REGISTRY, TOOL_SCHEMAS


class CodeReviewAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def run(self, user_input: str, max_rounds: int = 6) -> str:
        """执行一次完整的 Agent 循环，返回最终审查 JSON 字符串。"""
        self.messages.append({"role": "user", "content": user_input})

        for round_idx in range(max_rounds):
            try:
                response = self.llm.chat(messages=self.messages, tools=TOOL_SCHEMAS)
            except Exception as e:
                return json.dumps(
                    {"error": f"LLM 调用失败: {e}"}, ensure_ascii=False
                )

            assistant_msg = response.choices[0].message
            self.messages.append(assistant_msg.model_dump())

            # 没有工具调用 → 最终回答
            if not assistant_msg.tool_calls:
                return self._ensure_json(assistant_msg.content or "")

            # 有工具调用 → 逐个执行并回写结果
            for call in assistant_msg.tool_calls:
                name = call.function.name
                tool_result = self._execute_tool(name, call.function.arguments)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(tool_result, ensure_ascii=False),
                })

        return json.dumps(
            {"error": f"Agent 超过最大轮次 {max_rounds}，未能生成最终审查结果"},
            ensure_ascii=False,
        )

    def _execute_tool(self, name: str, arguments: str) -> dict:
        """安全执行工具：白名单 + 参数校验 + 异常兜底。"""
        if name not in TOOL_REGISTRY:
            return {"error": f"工具未注册，拒绝执行: {name}"}

        try:
            args = json.loads(arguments)
        except json.JSONDecodeError as e:
            return {"error": f"工具参数不是合法 JSON: {e}"}

        if not isinstance(args, dict):
            return {"error": "工具参数必须是 JSON 对象"}

        try:
            result = TOOL_REGISTRY[name](**args)
            if not isinstance(result, dict):
                return {"error": f"工具返回了非字典类型: {type(result)}"}
            return result
        except TypeError as e:
            return {"error": f"工具参数不匹配: {e}"}
        except Exception as e:
            return {"error": f"工具执行异常: {e}"}

    def _ensure_json(self, text: str) -> str:
        """确保最终输出是合法 JSON；如果模型偶尔带了代码块围栏，尝试剥离。"""
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if len(lines) >= 3:
                cleaned = "\n".join(lines[1:-1]).strip()
        try:
            json.loads(cleaned)
            return cleaned
        except json.JSONDecodeError:
            return json.dumps(
                {
                    "summary": "模型返回了非 JSON 内容，已原样保留，请检查 Prompt 或模型输出稳定性。",
                    "verdict": "comment",
                    "raw_output": text[:2000],
                    "issues": [],
                    "improved_code": None,
                },
                ensure_ascii=False,
            )

    def reset(self):
        """清空对话历史，开始新的审查会话。"""
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]