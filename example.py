"""
小白入门：跑通「Skill 识别 + 工具循环」的最小示例。

运行前：
  pip install langgraph langchain-core

运行：
  python example.py
"""

from agent import SkillAgent, SkillRegistry, ToolRegistry
from agent.skills.builtins import (
    CODE_REVIEW_SKILL,
    FEISHU_NOTIFY_SKILL,
    SEARCH_SKILL,
    calc,
    search_web,
)


def main():
    # 1) 注册「全局工具」—— 所有 skill 都可能用到的基础能力
    tools = ToolRegistry()
    tools.register(search_web)
    tools.register(calc)

    # 2) 注册「技能」—— 带描述、提示词、专属工具的能力包
    skills = SkillRegistry()
    skills.register(SEARCH_SKILL)
    skills.register(FEISHU_NOTIFY_SKILL)
    skills.register(CODE_REVIEW_SKILL)

    # 3) 组装 Agent（内部是一张 LangGraph）
    agent = SkillAgent(tools=tools, skills=skills, max_iterations=5)

    # 4) 跑一条会同时触发「搜索 + 计算」意图的用户话
    query = "帮我查一下 LangGraph 是什么，并计算 123 * 456"
    result = agent.run(query)

    print("===== 用户 =====")
    print(query)
    print("===== 识别到的 skill =====")
    print(result.get("active_skill"), result.get("skill_context"))
    print("===== 工具结果 =====")
    print(result.get("tool_results"))
    print("===== 最终回复 =====")
    last = result["messages"][-1]
    content = last["content"] if isinstance(last, dict) else getattr(last, "content", last)
    print(content)


if __name__ == "__main__":
    main()
