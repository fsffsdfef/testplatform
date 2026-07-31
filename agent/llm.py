"""
步骤5：LLM 适配层

为什么单独抽 llm.py？
- 业务节点不该关心「用哪家模型、有没有 API Key」。
- 小白阶段先提供一个「规则版伪 LLM」，不配 Key 也能跑通整张图。
- 以后换成 OpenAI / 本地模型，只改这里。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class FakeToolCall:
    """模仿常见 ChatModel 的 tool_call 结构，方便节点统一处理。"""

    name: str
    args: dict[str, Any]
    id: str = "call_1"


@dataclass
class FakeAIMessage:
    content: str
    tool_calls: list[FakeToolCall]

    def __post_init__(self) -> None:
        if self.tool_calls is None:
            self.tool_calls = []


class SimpleLLM:
    """极简决策器：根据文本规则决定「调工具」还是「直接回答」。

    设计原因：
    1. 让你先看懂 Agent 的控制流，而不是卡在 API Key / SDK 上。
    2. 真实项目把 chat() 换成 langchain ChatOpenAI 即可。
    """

    def chat(
        self,
        *,
        system: str,
        user_text: str,
        available_tools: list[str],
        tool_results: Optional[list[dict[str, Any]]] = None,
    ) -> FakeAIMessage:
        text = user_text or ""
        tool_results = tool_results or []
        done = {r.get("tool") for r in tool_results}

        # 需要搜索（若尚未执行过）
        need_search = "search_web" in available_tools and any(
            k in text for k in ("查", "是什么", "什么是", "搜索", "了解", "LangGraph", "langgraph")
        )
        if need_search and "search_web" not in done:
            return FakeAIMessage(
                content="",
                tool_calls=[FakeToolCall(name="search_web", args={"query": text})],
            )

        # 需要计算（若尚未执行过；支持「先搜再算」的多步）
        need_calc = "calc" in available_tools and re.search(r"\d+\s*[\*\+\-/]\s*\d+", text)
        if need_calc and "calc" not in done:
            m = re.search(r"(\d+\s*[\*\+\-/]\s*\d+(?:\s*[\*\+\-/]\s*\d+)*)", text)
            expr = m.group(1) if m else "1+1"
            return FakeAIMessage(
                content="",
                tool_calls=[FakeToolCall(name="calc", args={"expression": expr}, id="call_2")],
            )

        # 已有工具结果且没有更多待办 → 汇总成最终回答（避免无限循环）
        if tool_results:
            parts = [f"{r.get('tool')}: {r.get('result')}" for r in tool_results]
            return FakeAIMessage(
                content="根据工具结果：\n" + "\n".join(parts),
                tool_calls=[],
            )

        # 飞书通知
        if "notify_feishu" in available_tools and any(k in text for k in ("飞书", "通知", "提醒")):
            return FakeAIMessage(
                content="",
                tool_calls=[FakeToolCall(name="notify_feishu", args={"message": text})],
            )

        # 代码审查
        if "review_snippet" in available_tools and any(
            k in text.lower() for k in ("审查", "review", "代码", "bug")
        ):
            # 尝试从用户文本里抽出代码块；没有就整段送去审查
            code = text
            fence = re.search(r"```(?:\w+)?\n([\s\S]*?)```", text)
            if fence:
                code = fence.group(1)
            return FakeAIMessage(
                content="",
                tool_calls=[FakeToolCall(name="review_snippet", args={"code": code})],
            )

        # 默认：直接回答
        return FakeAIMessage(
            content=f"（未触发工具）系统提示摘要: {system[:40]}...；用户说: {text}",
            tool_calls=[],
        )


def message_text(messages: list[Any]) -> str:
    """从状态 messages 里取出最近一条用户/可读文本。"""
    for msg in reversed(messages or []):
        # dict 风格
        if isinstance(msg, dict):
            if msg.get("role") == "user":
                return str(msg.get("content") or "")
            continue
        # LangChain 风格
        role = getattr(msg, "type", None) or getattr(msg, "role", None)
        content = getattr(msg, "content", "")
        if role in ("human", "user"):
            return str(content)
    if not messages:
        return ""
    last = messages[-1]
    if isinstance(last, dict):
        return str(last.get("content") or "")
    return str(getattr(last, "content", last))


def dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)
