"""
步骤8：组装 LangGraph 图 + 对外 SkillAgent

整体拓扑（请在脑子里画出来）：

    START
      │
      ▼
  skill_router   ← 识别要用哪个 skill
      │
      ▼
  skill_entry    ← 加载该 skill 的提示词/工具名单
      │
      ▼
    planner      ← 决定：调工具 or 最终回答
      │
      ├──(有 tool_calls)──► tools ──► planner   （循环）
      │
      └──(无 tool_calls)──► END

为什么用「图」而不是 while True？
- 图把控制流可视化、可中断、可持久化（checkpoint）、可插入人工确认。
- 这正是 LangGraph 相对「手写循环 Agent」的优势。
"""

from __future__ import annotations

from typing import Any, Optional

from langgraph.graph import END, START, StateGraph

from agent.llm import SimpleLLM
from agent.nodes import (
    make_planner,
    make_skill_entry,
    make_skill_router,
    make_tools_node,
)
from agent.routing import after_planner
from agent.skills.registry import SkillRegistry
from agent.state import AgentState
from agent.tools.registry import ToolRegistry


def build_graph(
    *,
    skills: SkillRegistry,
    tools: Optional[ToolRegistry] = None,
    llm: Optional[SimpleLLM] = None,
    max_iterations: int = 5,
):
    tools = tools or ToolRegistry()
    llm = llm or SimpleLLM()

    graph = StateGraph(AgentState)

    # 注册节点：名字随便起，但要和边里引用的一致
    graph.add_node("skill_router", make_skill_router(skills))
    graph.add_node("skill_entry", make_skill_entry(skills))
    graph.add_node("planner", make_planner(llm, skills, tools, max_iterations))
    graph.add_node("tools", make_tools_node(skills, tools))

    # 固定边：识别 → 进入 → 规划
    graph.add_edge(START, "skill_router")
    graph.add_edge("skill_router", "skill_entry")
    graph.add_edge("skill_entry", "planner")

    # 条件边：规划后分支
    graph.add_conditional_edges(
        "planner",
        after_planner,
        {
            "tools": "tools",
            "__end__": END,
        },
    )

    # 工具执行完回到规划，形成 ReAct 风格循环
    graph.add_edge("tools", "planner")

    return graph.compile()


class SkillAgent:
    """给业务侧用的薄封装：屏蔽 LangGraph 细节。"""

    def __init__(
        self,
        *,
        skills: SkillRegistry,
        tools: Optional[ToolRegistry] = None,
        llm: Optional[SimpleLLM] = None,
        max_iterations: int = 5,
    ) -> None:
        self.skills = skills
        self.tools = tools or ToolRegistry()
        self.llm = llm or SimpleLLM()
        self.max_iterations = max_iterations
        self.app = build_graph(
            skills=skills,
            tools=self.tools,
            llm=self.llm,
            max_iterations=max_iterations,
        )

    def run(self, user_input: str) -> dict[str, Any]:
        """同步跑一轮完整图。"""
        initial: AgentState = {
            "messages": [{"role": "user", "content": user_input}],
            "active_skill": None,
            "skill_context": {},
            "tool_results": [],
            "iteration": 0,
        }
        return self.app.invoke(initial)
