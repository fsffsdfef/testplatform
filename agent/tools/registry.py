"""工具注册表：名字 → 可执行函数。"""

from __future__ import annotations

import json
from typing import Any, Callable


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Callable] = {}

    def register(self, fn: Callable) -> None:
        name = getattr(fn, "__name__", None)
        if not name:
            raise ValueError("工具必须是具名函数")
        self._tools[name] = fn

    def get(self, name: str) -> Callable | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools.keys())

    def run(self, name: str, arguments: dict[str, Any] | str) -> Any:
        fn = self.get(name)
        if fn is None:
            return {"error": f"未知工具: {name}"}
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments) if arguments else {}
            except json.JSONDecodeError:
                arguments = {"input": arguments}
        try:
            return fn(**(arguments or {}))
        except TypeError as e:
            return {"error": f"参数错误: {e}"}
        except Exception as e:  # noqa: BLE001
            return {"error": str(e)}
