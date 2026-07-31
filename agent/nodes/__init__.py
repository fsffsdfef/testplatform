"""
步骤6：图上的各个节点（Node）

为什么拆成多个节点，而不是一个大函数？
- 每个节点只做一件事，方便调试：「是路由错了，还是工具挂了？」
- LangGraph 的条件边可以在节点之间跳转，形成循环（Agent 的核心）。
"""

from __future__ import annotations

from typing import Any

from agent.llm import SimpleLLM, dumps, message_text
from agent.skills.registry import SkillRegistry
from agent.state import AgentState
from agent.tools.registry import ToolRegistry


def make_skill_router(skills: SkillRegistry):
    """节点 A：识别 skill。

    设计原因：
    - 先「选能力包」，再「执行」，比一上来把所有工具塞给模型更清晰。
    - 教学版用关键词打分；生产可改成 LLM 分类。
    """

    def skill_router(state: AgentState) -> dict[str, Any]:
        text = message_text(state.get("messages", []))
        best = None
        best_score = 0
        for skill in skills.all():
            score = skill.matches(text)
            if score > best_score:
                best = skill
                best_score = score

        if best is None:
            fallback = skills.get("search") or (skills.all()[0] if skills.all() else None)
            name = fallback.name if fallback else None
            reason = "无关键词命中，使用兜底 skill"
        else:
            name = best.name
            reason = f"关键词命中分数={best_score}"

        return {
            "active_skill": name,
            "skill_context": {"reason": reason, "user_text": text},
            "iteration": 0,
            "tool_results": [],
        }

    return skill_router


def make_skill_entry(skills: SkillRegistry):
    """节点 B：进入 skill（加载上下文）。

    设计原因：
    - 把「识别」和「加载」分开：router 只负责选名字，entry 负责取配置。
    - 以后要做权限校验、审计日志，也适合放在 entry。
    """

    def skill_entry(state: AgentState) -> dict[str, Any]:
        name = state.get("active_skill")
        skill = skills.get(name) if name else None
        ctx = dict(state.get("skill_context") or {})
        if skill:
            ctx["system_prompt"] = skill.system_prompt
            ctx["tool_names"] = [fn.__name__ for fn in skill.tools]
        else:
            ctx["system_prompt"] = "你是通用助手，用中文简洁回答。"
            ctx["tool_names"] = []
        return {"skill_context": ctx}

    return skill_entry


def make_planner(llm: SimpleLLM, skills: SkillRegistry, tools: ToolRegistry, max_iterations: int):
    """节点 C：规划下一步 —— 调工具 or 最终回答。

    设计原因：
    - Agent 的「智能」主要在这里：看对话 + 工具结果，决定下一步。
    - 用 iteration 做熔断，防止死循环把费用/CPU 打满。
    """

    def planner(state: AgentState) -> dict[str, Any]:
        iteration = int(state.get("iteration") or 0)
        if iteration >= max_iterations:
            return {
                "messages": [
                    {
                        "role": "assistant",
                        "content": f"已达到最大迭代次数 {max_iterations}，停止。",
                    }
                ]
            }

        skill = skills.get(state.get("active_skill") or "")
        system = (state.get("skill_context") or {}).get("system_prompt") or "你是助手。"
        available = list(tools.names())
        if skill:
            for fn in skill.tools:
                if fn.__name__ not in available:
                    available.append(fn.__name__)

        user_text = message_text(state.get("messages", []))
        ai = llm.chat(
            system=system,
            user_text=user_text,
            available_tools=available,
            tool_results=state.get("tool_results") or [],
        )

        if not ai.tool_calls:
            return {
                "messages": [{"role": "assistant", "content": ai.content}],
                "iteration": iteration + 1,
            }

        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": ai.content or "",
                    "tool_calls": [
                        {"name": tc.name, "args": tc.args, "id": tc.id} for tc in ai.tool_calls
                    ],
                }
            ],
            "iteration": iteration + 1,
        }

    return planner


def make_tools_node(skills: SkillRegistry, tools: ToolRegistry):
    """节点 D：真正执行工具。

    设计原因：
    - 模型只「提议」调用什么；真正执行必须在代码里做（安全、可审计）。
    - 执行结果写回 state.tool_results，下一轮 planner 才能看到。
    """

    def tools_node(state: AgentState) -> dict[str, Any]:
        messages = state.get("messages") or []
        last = messages[-1] if messages else {}
        if isinstance(last, dict):
            tool_calls = last.get("tool_calls") or []
        else:
            tool_calls = getattr(last, "tool_calls", None) or []

        runtime = ToolRegistry()
        for name in tools.names():
            fn = tools.get(name)
            if fn:
                runtime.register(fn)
        skill = skills.get(state.get("active_skill") or "")
        if skill:
            for fn in skill.tools:
                if fn.__name__ not in runtime.names():
                    runtime.register(fn)

        results = []
        result_messages = []
        for call in tool_calls:
            if isinstance(call, dict):
                name = call.get("name")
                args = call.get("args") or call.get("arguments") or {}
                call_id = call.get("id") or name
            else:
                name = getattr(call, "name", None)
                args = getattr(call, "args", {}) or {}
                call_id = getattr(call, "id", name)

            result = runtime.run(name, args)
            results.append({"tool": name, "args": args, "result": result})
            result_messages.append(
                {
                    "role": "tool",
                    "content": dumps(result),
                    "name": name,
                    "tool_call_id": call_id,
                }
            )

        # 追加而不是覆盖：多轮 tools→planner 时要保留历史结果
        prev = list(state.get("tool_results") or [])
        return {"tool_results": prev + results, "messages": result_messages}

    return tools_node
