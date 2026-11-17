from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_import_boundaries import Violation, find_violations


@pytest.mark.parametrize("module", [
    "nujinagent.agent.loop", "nujinagent.session.state", "nujinagent.runtime_admission",
    "nujinagent.data_access", "nujinagent.installation_lock",
])
def test_runtime_owners_do_not_depend_on_update_policy(module: str) -> None:
    assert find_violations("from nujinagent.update_service import UpdateService", module) == [
        Violation("update-policy-direction", "nujinagent.update_service.UpdateService", 1),
    ]


def test_updater_uses_process_contracts_not_agent_or_client_implementations() -> None:
    assert find_violations("from nujinagent.agent.loop import AgentLoop", "nujinagent.update_stop") == [
        Violation("update-domain", "nujinagent.agent.loop.AgentLoop", 1),
    ]
    assert find_violations(
        "from nujinagent.gateway.runtime import GatewayRuntime", "nujinagent.update_stop",
    ) == []
    assert find_violations(
        "from nujinagent.update_stop import watch_gateway_stop", "nujinagent.cli.gateway_runtime",
    ) == []
    assert find_violations(
        "from nujinagent.cli.gateway_runtime import _run_gateway", "nujinagent.update_restart",
    ) == []
    assert find_violations(
        "from nujinagent.agent.loop import AgentLoop", "nujinagent.update_restart",
    ) == [Violation("update-restart-adapter", "nujinagent.agent.loop.AgentLoop", 1)]


@pytest.mark.parametrize(
    ("source", "target", "line"),
    [
        ("import nujinagent.webui.metadata", "nujinagent.webui.metadata", 1),
        ("from nujinagent import webui", "nujinagent.webui", 1),
        ("from nujinagent.webui import metadata", "nujinagent.webui.metadata", 1),
        ("from .. import webui", "nujinagent.webui", 1),
        ("from ..webui import metadata", "nujinagent.webui.metadata", 1),
        (
            "def load():\n    from nujinagent.cli import gateway",
            "nujinagent.cli.gateway", 2,
        ),
        (
            "import importlib\nimportlib.import_module('nujinagent.webui.metadata')",
            "nujinagent.webui.metadata", 2,
        ),
        (
            "import importlib as modules\n"
            "modules.import_module(name='nujinagent.webui.metadata')",
            "nujinagent.webui.metadata", 2,
        ),
        (
            "from importlib import import_module as load\n"
            "load('..webui.metadata', __package__)",
            "nujinagent.webui.metadata", 2,
        ),
        (
            "from importlib import import_module\n"
            "import_module('..webui.metadata', package='nujinagent.agent')",
            "nujinagent.webui.metadata", 2,
        ),
        ("__import__('nujinagent.webui.metadata')", "nujinagent.webui.metadata", 1),
        (
            "import builtins as imports\nimports.__import__('nujinagent.webui.metadata')",
            "nujinagent.webui.metadata", 2,
        ),
    ],
)
def test_core_rejects_adapter_imports_in_supported_spellings(
    source: str, target: str, line: int,
) -> None:
    assert find_violations(source, "nujinagent.agent.loop") == [
        Violation("core-execution", target, line),
    ]


@pytest.mark.parametrize(
    "source",
    [
        "from typing import TYPE_CHECKING as TC\n"
        "if TC:\n    from nujinagent.webui import metadata",
        "import typing as t\n"
        "if t.TYPE_CHECKING:\n    from nujinagent.webui import metadata",
    ],
)
def test_core_boundary_includes_type_dependencies(source: str) -> None:
    assert find_violations(source, "nujinagent.agent.runner") == [
        Violation("core-execution", "nujinagent.webui.metadata", 3),
    ]


@pytest.mark.parametrize(
    ("module", "rule"),
    [
        ("nujinagent.session.manager", "session-storage"),
        ("nujinagent.session.recovery", "session-storage"),
        ("nujinagent.security.workspace_policy", "security-primitives"),
        ("nujinagent.agent.turn_delivery", "core-execution"),
        ("nujinagent.channels.notification_routes", "channel-routing-contracts"),
        ("nujinagent.config.schema", "configuration-contracts"),
        ("nujinagent.agent.tools.cli_apps_config", "tool-configuration-contracts"),
        ("nujinagent.utils.file_io", "shared-primitives"),
    ],
)
def test_storage_and_security_do_not_depend_on_adapters(module: str, rule: str) -> None:
    assert find_violations("from nujinagent.cli import gateway", module) == [
        Violation(rule, "nujinagent.cli.gateway", 1),
    ]


@pytest.mark.parametrize(
    "dependency",
    [
        "nujinagent.bus.outbound_events.ProgressEvent",
        "nujinagent.command.router",
        "nujinagent.pairing.events.PairingChanged",
        "nujinagent.session.webui_turns.clear_websocket_turn_if_current",
        "nujinagent.webui.transcript.WebUITranscriptRecorder",
        "nujinagent.webui.outbound_wire.project_notification",
    ],
)
def test_websocket_transport_leaves_event_and_history_policy_to_delivery(dependency: str) -> None:
    module, name = dependency.rsplit(".", 1)
    source = f"from {module} import {name}\n"
    assert find_violations(source, "nujinagent.channels.websocket.runtime") == [
        Violation("websocket-transport", dependency, 1),
    ]
    assert find_violations(source, "nujinagent.webui.outbound_delivery") == []


@pytest.mark.parametrize(
    "source",
    [
        "from nujinagent.config.schema import Base",
        "from ...config.schema import Base as ConfigBase",
    ],
)
def test_tool_configs_import_the_shared_base_directly(source: str) -> None:
    assert find_violations(source, "nujinagent.agent.tools.shell") == [
        Violation("tool-config-base", "nujinagent.config.schema.Base", 1),
    ]
    assert find_violations(
        "from nujinagent.config_base import Base", "nujinagent.agent.tools.shell",
    ) == []


def test_configuration_imports_the_six_tool_owned_config_contracts() -> None:
    source = (
        "from nujinagent.agent.tools.cli_apps_config import CliAppsToolConfig\n"
        "from nujinagent.agent.tools.filesystem_config import FileToolsConfig\n"
        "from nujinagent.agent.tools.image_generation_config import ImageGenerationToolConfig\n"
        "from nujinagent.agent.tools.self_config import MyToolConfig\n"
        "from nujinagent.agent.tools.shell_config import ExecToolConfig\n"
        "from nujinagent.agent.tools.web_config import WebToolsConfig\n"
    )
    assert find_violations(source, "nujinagent.config.schema") == []


@pytest.mark.parametrize(
    ("module", "source"),
    [
        ("nujinagent.agent.loop", "from nujinagent.session.recovery import RecoveryAdmission"),
        ("nujinagent.session.manager", "from nujinagent.providers.base import ProviderConversationState"),
        ("nujinagent.session.webui_turns", "from nujinagent.webui import transcript"),
        ("nujinagent.cli.gateway_runtime", "from nujinagent.agent.loop import AgentLoop"),
        ("nujinagent.channels.websocket.runtime", "from nujinagent.webui import inbound_commands"),
        ("nujinagent.agent.tools.cli_apps_config", "from nujinagent.config_base import Base"),
        (
            "nujinagent.agent.turn_delivery",
            "from nujinagent.channels.notification_routes import notification_metadata",
        ),
    ],
)
def test_existing_runtime_and_composition_dependencies_remain_allowed(
    module: str, source: str,
) -> None:
    assert find_violations(source, module) == []


@pytest.mark.parametrize(
    ("relative", "source", "rule", "target", "line"),
    [
        (
            "nujinagent/agent/runner.py", "import nujinagent.webui.metadata",
            "core-execution", "nujinagent.webui.metadata", 1,
        ),
        (
            "nujinagent/agent/loop.py",
            "import importlib\nif importlib.import_module('nujinagent.webui.metadata'):\n    pass",
            "core-execution", "nujinagent.webui.metadata", 2,
        ),
        (
            "nujinagent/agent/loop.py", "if __import__('nujinagent.webui.metadata'):\n    pass",
            "core-execution", "nujinagent.webui.metadata", 1,
        ),
        (
            "nujinagent/session/manager.py", "from nujinagent.cli import gateway",
            "session-storage", "nujinagent.cli.gateway", 1,
        ),
        (
            "nujinagent/channels/notification_routes.py",
            "from nujinagent.channels.slack.runtime import SlackChannel",
            "channel-routing-contracts", "nujinagent.channels.slack.runtime.SlackChannel", 1,
        ),
        (
            "nujinagent/channels/notification_routes.py",
            "from nujinagent.agent.turn_delivery import TurnRoute",
            "channel-routing-contracts", "nujinagent.agent.turn_delivery.TurnRoute", 1,
        ),
        (
            "nujinagent/security/__init__.py", "from ..cli import gateway",
            "security-primitives", "nujinagent.cli.gateway", 1,
        ),
        (
            "nujinagent/channels/websocket/runtime.py",
            "import importlib as modules\nmodules.import_module('nujinagent.command.router')",
            "websocket-transport", "nujinagent.command.router", 2,
        ),
        (
            "nujinagent/agent/tools/shell.py", "from ...config.schema import Base as ConfigBase",
            "tool-config-base", "nujinagent.config.schema.Base", 1,
        ),
        (
            "nujinagent/channels/telegram/runtime.py", "from nujinagent.config.schema import Base",
            "tool-config-base", "nujinagent.config.schema.Base", 1,
        ),
        (
            "nujinagent/config/schema.py", "from nujinagent.agent.tools.shell import ExecTool",
            "configuration-contracts", "nujinagent.agent.tools.shell.ExecTool", 1,
        ),
        (
            "nujinagent/agent/tools/cli_apps_config.py", "from .cli_apps import CliAppsTool",
            "tool-configuration-contracts", "nujinagent.agent.tools.cli_apps.CliAppsTool", 1,
        ),
        (
            "nujinagent/agent/tools/web_config.py", "from nujinagent.config.schema import Config",
            "tool-configuration-contracts", "nujinagent.config.schema.Config", 1,
        ),
        (
            "nujinagent/providers/oauth_catalog_cache.py",
            "from nujinagent.providers import openai_codex_provider",
            "oauth-catalog-cache", "nujinagent.providers.openai_codex_provider", 1,
        ),
    ],
)
def test_cli_rejects_a_violation_and_reports_its_source_location(
    tmp_path: Path, relative: str, source: str, rule: str, target: str, line: int,
) -> None:
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_text(source + "\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "scripts.check_import_boundaries", "--root", str(tmp_path)],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert result.stderr.strip() == f"{relative}:{line}: [{rule}] must not import {target}"


def test_cli_accepts_a_tool_owned_config_import(tmp_path: Path) -> None:
    path = tmp_path / "nujinagent/config/schema.py"
    path.parent.mkdir(parents=True)
    path.write_text(
        "from nujinagent.agent.tools.cli_apps_config import CliAppsToolConfig\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "-m", "scripts.check_import_boundaries", "--root", str(tmp_path)],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
