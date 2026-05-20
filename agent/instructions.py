from pydantic_ai import RunContext

from agent.dependencies import AgentDependencies


async def add_client_name(ctx: RunContext[AgentDependencies]) -> str:
    """Add clients's name to the agent's instructions."""
    client = await ctx.deps.db.get_client()
    return f"The client's name is {client.name}."
