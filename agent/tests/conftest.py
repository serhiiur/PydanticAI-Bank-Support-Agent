import logging
from unittest.mock import AsyncMock

import pytest
from pydantic_ai import models

from agent.dependencies import AgentDeps

# make sure we don't accidentally make real requests to the LLM while testing
models.ALLOW_MODEL_REQUESTS = False


@pytest.fixture
def mock_deps() -> AgentDeps:
    """Mock agent dependencies."""
    mock_db = AsyncMock()
    mock_currency = AsyncMock()
    return AgentDeps(
        db=mock_db,
        currency=mock_currency,
        logger=logging.getLogger("test"),
    )
