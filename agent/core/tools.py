from typing import Any

from pydantic_ai import RunContext, SkipToolExecution, ToolsetTool, WrapperToolset

from agent.core.exceptions import BaseAgentException


class BaseBankAgentToolset(WrapperToolset):
    """Custom wrapper for all bank's agent toolsets.

    It executes the given tool, and if it raises a subclass of BaseAgentException
    exception, returns its string message as the tool result.

    If unexpected exception is raised, logs the error and skips execution of the tool.

    See: https://pydantic.dev/docs/ai/tools-toolsets/toolsets/#changing-tool-execution
    """

    async def call_tool(
        self,
        name: str,
        tool_args: dict[str, Any],
        ctx: RunContext,
        tool: ToolsetTool,
    ) -> Any:
        try:
            return await super().call_tool(name, tool_args, ctx, tool)
        except BaseAgentException as e:
            return str(e)
        except Exception as e:
            # ctx.deps.logger.error("Internal Server Error: %s", str(e))
            raise SkipToolExecution("Agent is currently unavailable") from e
