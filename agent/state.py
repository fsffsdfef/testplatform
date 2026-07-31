"""
步骤1：定义 Agent 的「共享状态」

为什么需要 State？
- LangGraph 把一次对话当成一张「流程图」来跑。
- 每个节点（函数）都会读/写同一份状态，就像接力跑时传递的接力棒。
- 没有 State，节点之间就无法共享「用户说了什么、选了哪个 skill、工具结果是什么」。
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, Optional, TypedDict


class AgentState(TypedDict):
    """Agent 在整张图里流转的数据。

    messages:
        对话历史。用 operator.add 做「列表拼接」，节点每次只返回「新增的消息」。
        原因：多轮对话需要保留上下文，工具调用也要追加到消息列表。

    active_skill:
        当前识别并激活的 skill 名称。
        原因：后续节点要根据 skill 切换提示词和可用工具。

    skill_context:
        skill 相关的补充信息（例如匹配理由、参数）。
        原因：方便调试，也方便 skill 内部使用。

    tool_results:
        最近一次工具执行结果。
        原因：planner 需要看到工具返回值，再决定继续调工具还是给最终回答。

    iteration:
        当前循环次数。
        原因：防止「工具→规划→工具」死循环，到上限就强制结束。
    """

    messages: Annotated[list, operator.add]
    active_skill: Optional[str]
    skill_context: dict[str, Any]
    tool_results: list[dict[str, Any]]
    iteration: int
