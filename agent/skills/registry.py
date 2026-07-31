"""
步骤3：Skill 注册表

为什么需要 Registry？
- Agent 启动时把所有 skill「登记」起来。
- 路由节点只和 Registry 打交道，不知道具体有多少个 skill。
- 好处：以后新增 skill，不用改图结构，只需 register 一次。
"""

from __future__ import annotations

from typing import Optional

from agent.skills.base import Skill


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        if skill.name in self._skills:
            raise ValueError(f"skill 已存在: {skill.name}")
        self._skills[skill.name] = skill

    def get(self, name: str) -> Optional[Skill]:
        return self._skills.get(name)

    def all(self) -> list[Skill]:
        return list(self._skills.values())

    def catalog_text(self) -> str:
        """生成给模型/规则路由看的技能目录。"""
        lines = []
        for s in self.all():
            lines.append(f"- {s.name}: {s.description}")
        return "\n".join(lines) if lines else "(暂无技能)"
