# Find the owning code

Choose the affected behavior below, then read its owner and existing tests. Follow only the relevant links; this is a task index, not a required reading list. Search the selected area for the user-visible operation before expanding to callers and shared contracts.

| Change | Start here | Existing coverage |
| --- | --- | --- |
| Browser input, pairing, navigation, history, or settings | [WebUI change map](../webui/README.md#change-a-behavior) | The map pairs each behavior with component and browser tests |
| Terminal input, menus, or rendering | [TUI source layout](../tui/README.md#source-layout) | Colocated tests; application interactions in [`tui/src/app/`](../tui/src/app/) |
| A chat channel or its setup UI | [Channel package guide](../docs/channel-package-guide.md), then its package in [`nujinagent/channels/`](../nujinagent/channels/) | The channel's own `tests/`, including `tests/webui/`; shared contracts in [`tests/channels/`](../tests/channels/) |
| Provider selection or model requests | [Provider extension guide](../docs/development.md#adding-an-llm-provider), [`providers/routing.py`](../nujinagent/providers/routing.py), then the selected adapter | [`tests/providers/`](../tests/providers/) |
| A tool's arguments or execution | The implementation and adjacent configuration in [`agent/tools/`](../nujinagent/agent/tools/); [`base.py`](../nujinagent/agent/tools/base.py) for the shared contract | [`tests/tools/`](../tests/tools/); runtime/session tools in [`tests/agent/tools/`](../tests/agent/tools/) |
| Shell process launch or cleanup | [`execution/processes.py`](../nujinagent/execution/processes.py) owns native process trees; [`agent/tools/exec_session.py`](../nujinagent/agent/tools/exec_session.py) owns session state and output | [`test_exec_platform.py`](../tests/tools/test_exec_platform.py), [`test_shell_reap.py`](../tests/tools/test_shell_reap.py), [`test_shell_execution_budgets.py`](../tests/tools/test_shell_execution_budgets.py) |
| Outbound HTTP redirects for fetched content | [`execution/http.py`](../nujinagent/execution/http.py) owns the GET and response lifetime; [`security/network.py`](../nujinagent/security/network.py) owns URL policy and DNS validation | [`test_web_fetch_security.py`](../tests/tools/test_web_fetch_security.py), [`test_image_generation_security.py`](../tests/providers/test_image_generation_security.py) |
| Slash commands or command dispatch | [`command/router.py`](../nujinagent/command/router.py), [`command/builtin.py`](../nujinagent/command/builtin.py) | [`tests/command/`](../tests/command/) |
| Turn scheduling, cancellation, or delivery | [`agent/loop.py`](../nujinagent/agent/loop.py), [`agent/turn_delivery.py`](../nujinagent/agent/turn_delivery.py) | [`test_loop_concurrency.py`](../tests/agent/test_loop_concurrency.py), [`test_task_cancel.py`](../tests/agent/test_task_cancel.py), [`test_turn_delivery.py`](../tests/agent/test_turn_delivery.py) |
| Model/tool iterations, retry, or injected input | [`agent/runner.py`](../nujinagent/agent/runner.py); [`agent/pending_inputs.py`](../nujinagent/agent/pending_inputs.py) owns run-local input batches and terminal waits, while `AgentLoop` prepares each input | [`test_runner_core.py`](../tests/agent/test_runner_core.py), [`test_runner_fallback.py`](../tests/agent/test_runner_fallback.py), [`test_runner_injections.py`](../tests/agent/test_runner_injections.py) |
| Prompt assembly, skills, or context limits | [`agent/context.py`](../nujinagent/agent/context.py), [`agent/context_governance.py`](../nujinagent/agent/context_governance.py); [prompt cautions](gotchas.md#prompt-templates) | [`test_context_builder.py`](../tests/agent/test_context_builder.py), [`test_skills_loader.py`](../tests/agent/test_skills_loader.py), [`test_context_governance.py`](../tests/agent/test_context_governance.py) |
| Session persistence or recovery | [`session/state.py`](../nujinagent/session/state.py), [`session/sqlite_store.py`](../nujinagent/session/sqlite_store.py), [`session/recovery.py`](../nujinagent/session/recovery.py) | [`tests/session/`](../tests/session/), [`test_loop_recovery.py`](../tests/agent/test_loop_recovery.py) |
| WebUI/TUI wire events or displayed history | [`webui/outbound_delivery.py`](../nujinagent/webui/outbound_delivery.py), [`webui/transcript.py`](../nujinagent/webui/transcript.py); [client compatibility](review-guide.md) | [`tests/webui/`](../tests/webui/), [`WebSocket tests`](../nujinagent/channels/websocket/tests/), and affected client tests |
| Workspace access or sandbox enforcement | [`security/workspace_access.py`](../nujinagent/security/workspace_access.py), [`execution/files.py`](../nujinagent/execution/files.py), [`execution/sandbox.py`](../nujinagent/execution/sandbox.py); [security rules](security.md) | [`tests/security/`](../tests/security/), [`test_workspace_scope.py`](../tests/agent/test_workspace_scope.py), [`test_sandbox.py`](../tests/tools/test_sandbox.py) |
| Gateway startup, shutdown, or launchers | [`gateway/`](../nujinagent/gateway/), [`cli/gateway_runtime.py`](../nujinagent/cli/gateway_runtime.py) | [`tests/gateway/`](../tests/gateway/), the matching launcher tests in [`tests/cli/`](../tests/cli/) |

For the end-to-end runtime flow, expand to [Architecture](../docs/architecture.md). For ownership changes, read [Design Constraints](design.md); directory proximity does not permit crossing those boundaries.

## Find the smallest useful check

Start with an existing test that exercises the changed operation and its relevant failure or lifecycle edge. File names above are entry points, not an exhaustive acceptance list. Keep integration coverage when the change crosses owners.

| Surface | Focused command | Setup and full checks |
| --- | --- | --- |
| Python | From the root: `uv run --no-sync python -m pytest tests/path/test_feature.py` | [Contribution setup](../CONTRIBUTING.md#development-setup), including channel dependencies for strict checking |
| WebUI | From `webui/`: `bun run test src/tests/feature.test.tsx` | [WebUI checks](../webui/README.md#test); channel UI tests are included by the same configuration |
| Browser | From `webui/`: `bun run test:browser browser/feature.spec.ts` | [WebUI checks](../webui/README.md#test) and the existing fixture for the affected interaction |
| TUI | From `tui/`: `bun test src/feature/feature.test.ts` | [TUI checks](../tui/README.md); terminal behavior still needs its real terminal path |

The command paths in this table are placeholders: substitute the selected existing file. Respect the task's local/remote verification boundary. Focused checks shorten feedback; they do not replace the required CI checks selected by [the workflow](../.github/workflows/ci.yml) and [its path rules](../scripts/ci_scope.py).
