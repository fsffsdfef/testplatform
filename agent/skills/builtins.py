"""
步骤4：内置示例工具 / 技能

为什么 Tool 也要 Registry？
- LangGraph 的「工具调用」需要：名字 → 可执行函数。
- 全局工具 + skill 专属工具可以合并后交给执行节点。
"""

from __future__ import annotations

from agent.skills.base import Skill


def search_web(query: str) -> dict:
    """假装搜索。真实项目里这里调搜索 API。"""
    demo = {
        "langgraph": "LangGraph 是 LangChain 生态里用「图」编排 Agent 工作流的库。",
        "langgraph 是什么": "LangGraph 用节点+边描述 Agent，支持循环、分支、人机协作。",
    }
    key = (query or "").strip().lower()
    for k, v in demo.items():
        if k in key:
            return {"query": query, "answer": v}
    return {"query": query, "answer": f"(演示) 未命中知识库，原始查询: {query}"}


def calc(expression: str) -> dict:
    """安全一点的四则运算演示（仅允许数字和 +-*/()）。"""
    allowed = set("0123456789+-*/(). %")
    expr = (expression or "").strip()
    if not expr or any(ch not in allowed for ch in expr):
        return {"error": "只允许数字和 +-*/().% "}
    try:
        return {"expression": expr, "result": eval(expr, {"__builtins__": {}}, {})}  # noqa: S307
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


def notify_feishu(message: str) -> dict:
    """假装发飞书。真实项目里调用飞书 webhook。"""
    return {"ok": True, "channel": "feishu", "message": message}


def review_snippet(code: str) -> dict:
    """假装代码审查。真实项目里可接静态分析或 LLM。"""
    hints = []
    if "eval(" in code:
        hints.append("避免使用 eval，存在安全风险")
    if "password" in code.lower() and ("=" in code):
        hints.append("疑似硬编码密码，建议改为环境变量/密钥管理")
    if not hints:
        hints.append("未发现明显问题（演示规则很少，仅供示例）")
    return {"findings": hints, "lines": len(code.splitlines())}


SEARCH_SKILL = Skill(
    name="search",
    description="当用户要查询概念、资料、是什么/怎么样时使用",
    system_prompt=(
        "你是检索助手。优先调用 search_web 获取信息，再给出简洁中文回答。"
        "如果还需要计算，可以调用 calc。"
    ),
    tools=[search_web, calc],
    keywords=("查", "搜索", "是什么", "什么是", "了解", "langgraph", "资料"),
)

FEISHU_NOTIFY_SKILL = Skill(
    name="feishu_notify",
    description="当用户要发飞书通知、提醒、群消息时使用",
    system_prompt="你是通知助手。把用户要发送的内容整理后调用 notify_feishu。",
    tools=[notify_feishu],
    keywords=("飞书", "通知", "提醒", "发消息", "webhook"),
)

CODE_REVIEW_SKILL = Skill(
    name="code_review",
    description="当用户要做代码审查、找 bug、看代码质量时使用",
    system_prompt="你是代码审查助手。先调用 review_snippet，再总结风险与建议。",
    tools=[review_snippet],
    keywords=("审查", "code review", "代码", "review", "bug", "质量"),
)
