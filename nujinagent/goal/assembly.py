"""Assemble the built-in sustained-goal feature at application entrypoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nujinagent.goal.command import register_goal_command
from nujinagent.goal.runtime import GOAL_GENERATION_VOLATILE_KEYS, GoalExecutionPolicy
from nujinagent.goal.tools import CreateGoalTool, UpdateGoalTool

if TYPE_CHECKING:
    from nujinagent.agent.tools.registry import ToolRegistry
    from nujinagent.bus.queue import MessageBus
    from nujinagent.command.router import CommandRouter
    from nujinagent.session.manager import SessionManager


def install_goal(
    sessions: SessionManager, bus: MessageBus, tools: ToolRegistry, commands: CommandRouter,
) -> GoalExecutionPolicy:
    register_goal_command(commands)
    sessions.exclude_generation_metadata(GOAL_GENERATION_VOLATILE_KEYS)
    for tool in (CreateGoalTool.bind(sessions, bus), UpdateGoalTool.bind(sessions, bus)):
        if not tools.has(tool.name):
            tools.register(tool)
    return GoalExecutionPolicy(sessions.state)
