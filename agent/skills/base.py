"""
步骤2：定义 Skill（技能）是什么

为什么要有 Skill？
- 普通 Agent 只有一套系统提示词 + 全部工具，容易「什么都会一点，但什么都不精」。
- Skill 把「某类任务」打包成：名称 + 描述 + 专用提示词 + 专用工具。
- 识别 Skill 后，Agent 只带上相关能力，更稳、更省 token、更好控制。

类比：
- 工具（Tool）= 电钻、锤子（具体动作）
- 技能（Skill）= 「木工套装」（包含说明文档 + 几件合适的工具）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass(frozen=True)
class Skill:
    """一个可被识别、可被激活的能力包。"""

    name: str
    """技能唯一标识，例如 code_review。"""

    description: str
    """给「路由节点」看的说明：什么时候该选这个 skill。
    原因：识别 skill 本质是「意图匹配」，描述写得越清楚，匹配越准。"""

    system_prompt: str
    """进入该 skill 后注入的系统提示词。
    原因：让模型用「该领域专家」的口吻和步骤工作。"""

    tools: list[Callable] = field(default_factory=list)
    """该 skill 可用的工具列表。
    原因：限制工具范围，避免模型乱调无关工具。"""

    keywords: tuple[str, ...] = ()
    """可选关键词，做轻量规则匹配。
    原因：小白阶段不必一上来就用大模型做路由，关键词更快、更可控、零成本。"""

    def matches(self, text: str) -> int:
        """返回匹配分数：命中关键词越多，分越高。

        为什么用简单打分而不是复杂 NLP？
        - 教学示例要先保证「可解释、可调试」。
        - 后面你可以轻松替换成 LLM 路由。
        """
        lower = (text or "").lower()
        return sum(1 for kw in self.keywords if kw.lower() in lower)
