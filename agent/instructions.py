from pydantic_ai import RunContext

from agent.dependencies import AgentDeps
from agent.exceptions import ClientNotFound


async def add_client_name(ctx: RunContext[AgentDeps]) -> str:
    """Add clients's name to the agent's instructions.

    If the client can't be identified, the corresponding message
    will be returned.

    :param ctx: Agent's context
    :return: string containing client's name or error message
    """
    try:
        client = await ctx.deps.db.get_client()
    except ClientNotFound as e:
        return str(e)
    return f"The client's name is {client.name}."
