from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from nujinagent.config.errors import ConfigIssue, ConfigLoadError
    from nujinagent.config.loader import get_config_path, load_config
    from nujinagent.config.paths import (
        get_cli_history_path,
        get_cron_dir,
        get_data_dir,
        get_legacy_sessions_dir,
        get_logs_dir,
        get_media_dir,
        get_runtime_subdir,
        get_webui_dir,
        get_workspace_path,
        is_default_workspace,
    )
    from nujinagent.config.schema import Config


_EXPORTS = {
    "Config": "nujinagent.config.schema",
    "ConfigIssue": "nujinagent.config.errors",
    "ConfigLoadError": "nujinagent.config.errors",
    "load_config": "nujinagent.config.loader",
    "get_config_path": "nujinagent.config.loader",
    "get_data_dir": "nujinagent.config.paths",
    "get_runtime_subdir": "nujinagent.config.paths",
    "get_media_dir": "nujinagent.config.paths",
    "get_cron_dir": "nujinagent.config.paths",
    "get_logs_dir": "nujinagent.config.paths",
    "get_webui_dir": "nujinagent.config.paths",
    "get_workspace_path": "nujinagent.config.paths",
    "is_default_workspace": "nujinagent.config.paths",
    "get_cli_history_path": "nujinagent.config.paths",
    "get_legacy_sessions_dir": "nujinagent.config.paths",
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
    "Config",
    "ConfigIssue",
    "ConfigLoadError",
    "load_config",
    "get_config_path",
    "get_data_dir",
    "get_runtime_subdir",
    "get_media_dir",
    "get_cron_dir",
    "get_logs_dir",
    "get_webui_dir",
    "get_workspace_path",
    "is_default_workspace",
    "get_cli_history_path",
    "get_legacy_sessions_dir",
]
