from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from nujinagent.agent.tools.base import Schema, Tool, ToolResult, tool_parameters
    from nujinagent.agent.tools.context import ToolContext
    from nujinagent.agent.tools.loader import ToolLoader
    from nujinagent.agent.tools.registry import ToolRegistry
    from nujinagent.agent.tools.schema import (
        ArraySchema,
        BooleanSchema,
        IntegerSchema,
        NumberSchema,
        ObjectSchema,
        StringSchema,
        tool_parameters_schema,
    )


_EXPORTS = {
    "Schema": "nujinagent.agent.tools.base",
    "ArraySchema": "nujinagent.agent.tools.schema",
    "BooleanSchema": "nujinagent.agent.tools.schema",
    "IntegerSchema": "nujinagent.agent.tools.schema",
    "NumberSchema": "nujinagent.agent.tools.schema",
    "ObjectSchema": "nujinagent.agent.tools.schema",
    "StringSchema": "nujinagent.agent.tools.schema",
    "Tool": "nujinagent.agent.tools.base",
    "ToolContext": "nujinagent.agent.tools.context",
    "ToolLoader": "nujinagent.agent.tools.loader",
    "ToolResult": "nujinagent.agent.tools.base",
    "ToolRegistry": "nujinagent.agent.tools.registry",
    "tool_parameters": "nujinagent.agent.tools.base",
    "tool_parameters_schema": "nujinagent.agent.tools.schema",
}


def __getattr__(name: str) -> Any:
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_EXPORTS))


__all__ = [
    "Schema",
    "ArraySchema",
    "BooleanSchema",
    "IntegerSchema",
    "NumberSchema",
    "ObjectSchema",
    "StringSchema",
    "Tool",
    "ToolContext",
    "ToolLoader",
    "ToolResult",
    "ToolRegistry",
    "tool_parameters",
    "tool_parameters_schema",
]
