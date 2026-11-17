from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from nujinagent.agent.context import ContextBuilder
    from nujinagent.agent.hook import (
        AgentHook,
        AgentHookContext,
        AgentRunHookContext,
        AgentTurnHookContext,
        AgentTurnHookFactory,
        CompositeHook,
    )
    from nujinagent.agent.loop import AgentLoop
    from nujinagent.agent.memory import MemoryStore
    from nujinagent.agent.skills import SkillsLoader
    from nujinagent.agent.subagent import SubagentManager


_EXPORTS = {
    "AgentHook": "nujinagent.agent.hook",
    "AgentHookContext": "nujinagent.agent.hook",
    "AgentRunHookContext": "nujinagent.agent.hook",
    "AgentTurnHookContext": "nujinagent.agent.hook",
    "AgentTurnHookFactory": "nujinagent.agent.hook",
    "AgentLoop": "nujinagent.agent.loop",
    "CompositeHook": "nujinagent.agent.hook",
    "ContextBuilder": "nujinagent.agent.context",
    "MemoryStore": "nujinagent.agent.memory",
    "SkillsLoader": "nujinagent.agent.skills",
    "SubagentManager": "nujinagent.agent.subagent",
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
    "AgentHook",
    "AgentHookContext",
    "AgentRunHookContext",
    "AgentTurnHookContext",
    "AgentTurnHookFactory",
    "AgentLoop",
    "CompositeHook",
    "ContextBuilder",
    "MemoryStore",
    "SkillsLoader",
    "SubagentManager",
]
