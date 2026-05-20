import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TypedDict

import uvicorn
from anyio import create_task_group, run, sleep, to_thread
from httpx import AsyncClient

# import logfire
from pydantic_ai import Agent
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy.ext.asyncio import AsyncSession

from agent.core.database.engine import async_session, engine
from agent.core.settings import settings
from agent.dependencies import AgentDependencies
from agent.instructions import add_client_name
from agent.output import AgentOutput
from agent.services.bank_db import BankDatabaseService
from agent.services.currency import CurrencyService
from agent.tools import bank_toolsets

# Configure Logfire to interact with Pydantic AI
# logfire.configure()
# logfire.instrument_pydantic_ai()

# Configure the Pydantic AI agent
agent = Agent.from_file(
    settings.agent_spec_filepath,
    deps_type=AgentDependencies,
    output_type=AgentOutput,
    toolsets=[*bank_toolsets],
)
agent.instructions(add_client_name)


class AgentLifespanState(TypedDict):
    """Agent's lifespan objects."""

    db_session: AsyncSession
    http_client: AsyncClient


@asynccontextmanager
async def agent_lifespan() -> AsyncIterator[AgentLifespanState]:
    """Lifespan bound to the agent."""
    async with async_session() as db_session, AsyncClient() as http_client:
        yield AgentLifespanState(db_session=db_session, http_client=http_client)
    await engine.dispose()


def run_web_agent(deps: AgentDependencies) -> None:
    """Run the agent in the Web mode using Uvicorn."""
    web_agent = agent.to_web(deps=deps)
    uvicorn.run(web_agent, access_log=False)


async def run_cli_agent(deps: AgentDependencies) -> None:
    """Run the agent in the CLI mode."""
    await sleep(1)
    await agent.to_cli(deps=deps)


async def main() -> None:
    """Run agent in the Web and CLI modes."""
    client_phone_number = PhoneNumber("+1 650-253-0000")
    currency_api_url = settings.currency.api_url
    async with agent_lifespan() as ls, create_task_group() as tg:
        deps = AgentDependencies(
            db=BankDatabaseService(ls["db_session"], client_phone_number),
            currency=CurrencyService(currency_api_url, ls["http_client"]),
            logger=logging.getLogger("pydantic_ai"),
        )
        tg.start_soon(run_cli_agent, deps)
        tg.start_soon(to_thread.run_sync, run_web_agent, deps)


if __name__ == "__main__":
    run(main, backend_options={"debug": settings.debug})
