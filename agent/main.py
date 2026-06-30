import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

import anyio

# import logfire
from anyio import to_thread
from httpx import AsyncClient
from pydantic_ai import Agent
from sqlalchemy.ext.asyncio import AsyncSession
from uvicorn import Config, Server

from agent.cli import AgentArgs, parse_args
from agent.core.database.engine import async_session, engine
from agent.core.settings import settings
from agent.dependencies import AgentDeps
from agent.instructions import add_client_name
from agent.output import AgentOutput
from agent.services.bank_db import BankDatabaseService
from agent.services.currency import CurrencyService
from agent.tools import bank_toolsets

# logfire.configure()
# logfire.instrument_pydantic_ai()

agent = Agent.from_file(
    settings.agent_spec_filepath,
    deps_type=AgentDeps,
    output_type=AgentOutput,
    toolsets=[*bank_toolsets],
)
agent.instructions(add_client_name)


@dataclass
class AgentLifespanState:
    """Agent's lifespan objects."""

    db_session: AsyncSession
    http_client: AsyncClient


@asynccontextmanager
async def lifespan() -> AsyncIterator[AgentLifespanState]:
    """Lifespan bound to the agent."""
    async with async_session() as db_session, AsyncClient() as http_client:
        yield AgentLifespanState(db_session, http_client)
    await engine.dispose()


async def run_agent_cli(deps: AgentDeps, server: Server | None) -> None:
    """Run the agent in the CLI mode."""
    # mimic delay to let the server (if WEB mode is enabled) start first
    await anyio.sleep(1)
    await agent.to_cli(deps=deps)
    # graceful shutdown for the agent running in WEB mode using /exit command
    if server is not None:
        server.should_exit = True


async def main(args: AgentArgs) -> None:
    """Run the agent."""
    async with lifespan() as ls, anyio.create_task_group() as tg:
        deps = AgentDeps(
            db=BankDatabaseService(ls.db_session),
            currency=CurrencyService(settings.currency.api_url, ls.http_client),
            logger=logging.getLogger("pydantic_ai"),
        )
        server = None
        if args.web:
            app = agent.to_web(deps=deps)
            server = Server(Config(app, args.host, args.port))
            tg.start_soon(to_thread.run_sync, server.run)
        if args.cli:
            tg.start_soon(run_agent_cli, deps, server)


if __name__ == "__main__":
    args = parse_args()
    anyio.run(main, args, backend_options={"debug": settings.debug})
