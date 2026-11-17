from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from nujinagent.llm_usage.models import LLMCallRecord
    from nujinagent.llm_usage.service import (
        empty_usage_payload,
        get_llm_usage_store,
        llm_usage_payload,
        llm_usage_store_path,
        record_llm_call,
    )
    from nujinagent.llm_usage.store import LLMUsageStore

_EXPORTS = {
    "LLMCallRecord": "nujinagent.llm_usage.models",
    "LLMUsageStore": "nujinagent.llm_usage.store",
    "empty_usage_payload": "nujinagent.llm_usage.service",
    "get_llm_usage_store": "nujinagent.llm_usage.service",
    "record_llm_call": "nujinagent.llm_usage.service",
    "llm_usage_store_path": "nujinagent.llm_usage.service",
    "llm_usage_payload": "nujinagent.llm_usage.service",
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
    "LLMCallRecord",
    "LLMUsageStore",
    "empty_usage_payload",
    "get_llm_usage_store",
    "record_llm_call",
    "llm_usage_store_path",
    "llm_usage_payload",
]
