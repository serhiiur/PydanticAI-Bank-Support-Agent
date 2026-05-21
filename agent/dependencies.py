from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    from agent.services.bank_db import BankDatabaseService
    from agent.services.currency import CurrencyService


@dataclass
class AgentDeps:
    """Dependencies to be used by the agent."""

    db: "BankDatabaseService"
    currency: "CurrencyService"
    logger: "Logger"
