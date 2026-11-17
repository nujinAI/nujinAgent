import tomllib
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .agent.tools.context import RequestContext
    from .bus.runtime_events import SessionTurnPersisted
    from .nujinagent import (
        STREAM_EVENT_REASONING_COMPLETED,
        STREAM_EVENT_REASONING_DELTA,
        STREAM_EVENT_RUN_COMPLETED,
        STREAM_EVENT_RUN_FAILED,
        STREAM_EVENT_RUN_STARTED,
        STREAM_EVENT_TEXT_COMPLETED,
        STREAM_EVENT_TEXT_DELTA,
        STREAM_EVENT_TOOL_COMPLETED,
        STREAM_EVENT_TOOL_FAILED,
        STREAM_EVENT_TOOL_STARTED,
        STREAM_EVENT_TYPES,
        LLMUsage,
        NujinAgent,
        RunResult,
        RunStream,
        SessionInfo,
        SessionSnapshot,
        StreamEvent,
        StreamEventType,
    )
    from .runtime_context import RuntimeContextBlock, RuntimeContextProvider


def _read_pyproject_version() -> str | None:
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    if not pyproject.exists():
        return None
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    return data.get("project", {}).get("version")


def _resolve_version() -> str:
    try:
        return _pkg_version("nujinagent")
    except PackageNotFoundError:
        # Source checkouts often import nujinagent without installed dist-info.
        return _read_pyproject_version() or "0.4.1"


__version__ = _resolve_version()
__logo__ = "🐈"

_LAZY_EXPORTS = {
    "NujinAgent": ".nujinagent",
    "LLMUsage": ".llm_usage.types",
    "RunStream": ".nujinagent",
    "RunResult": ".nujinagent",
    "RequestContext": ".agent.tools.context",
    "RuntimeContextBlock": ".runtime_context",
    "RuntimeContextProvider": ".runtime_context",
    "SessionInfo": ".nujinagent",
    "SessionSnapshot": ".nujinagent",
    "STREAM_EVENT_REASONING_COMPLETED": ".nujinagent",
    "STREAM_EVENT_REASONING_DELTA": ".nujinagent",
    "STREAM_EVENT_RUN_COMPLETED": ".nujinagent",
    "STREAM_EVENT_RUN_FAILED": ".nujinagent",
    "STREAM_EVENT_RUN_STARTED": ".nujinagent",
    "STREAM_EVENT_TEXT_COMPLETED": ".nujinagent",
    "STREAM_EVENT_TEXT_DELTA": ".nujinagent",
    "STREAM_EVENT_TOOL_COMPLETED": ".nujinagent",
    "STREAM_EVENT_TOOL_FAILED": ".nujinagent",
    "STREAM_EVENT_TOOL_STARTED": ".nujinagent",
    "STREAM_EVENT_TYPES": ".nujinagent",
    "StreamEvent": ".nujinagent",
    "StreamEventType": ".nujinagent",
    "SessionTurnPersisted": ".bus.runtime_events",
}


def __getattr__(name: str) -> Any:
    module_path = _LAZY_EXPORTS.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module
    mod = import_module(module_path, __name__)
    val = getattr(mod, name)
    globals()[name] = val
    return val


__all__ = [
    "NujinAgent",
    "LLMUsage",
    "RunResult",
    "RequestContext",
    "RuntimeContextBlock",
    "RuntimeContextProvider",
    "RunStream",
    "SessionInfo",
    "SessionSnapshot",
    "STREAM_EVENT_REASONING_COMPLETED",
    "STREAM_EVENT_REASONING_DELTA",
    "STREAM_EVENT_RUN_COMPLETED",
    "STREAM_EVENT_RUN_FAILED",
    "STREAM_EVENT_RUN_STARTED",
    "STREAM_EVENT_TEXT_COMPLETED",
    "STREAM_EVENT_TEXT_DELTA",
    "STREAM_EVENT_TOOL_COMPLETED",
    "STREAM_EVENT_TOOL_FAILED",
    "STREAM_EVENT_TOOL_STARTED",
    "STREAM_EVENT_TYPES",
    "StreamEvent",
    "StreamEventType",
    "SessionTurnPersisted",
]
