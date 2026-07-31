"""
步骤7：条件路由（Conditional Edges）

为什么需要路由函数？
- 普通边是「A 做完一定去 B」。
- 条件边是「看状态再决定去哪」—— Agent 的循环就靠它：
  planner 后：有工具调用 → tools；没有 → 结束。
"""

from __future__ import annotations

from typing import Any, Literal

from agent.state import AgentState


def after_planner(state: AgentState) -> Literal["tools", "__end__"]:
    messages = state.get("messages") or []
    if not messages:
        return "__end__"
    last: Any = messages[-1]
    tool_calls = []
    if isinstance(last, dict):
        # 最终回答消息没有 tool_calls
        if last.get("role") == "assistant" and last.get("tool_calls"):
            tool_calls = last["tool_calls"]
    else:
        tool_calls = getattr(last, "tool_calls", None) or []

    return "tools" if tool_calls else "__end__"
