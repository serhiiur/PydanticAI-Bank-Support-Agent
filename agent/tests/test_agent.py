from pydantic_ai.models.test import TestModel
from pydantic_extra_types.phone_numbers import PhoneNumber

from agent.dependencies import AgentDeps
from agent.main import agent
from agent.models import Client
from agent.output import AgentOutput


async def test_agent_returns_structured_output(mock_deps: AgentDeps) -> None:
    """Agent returns a valid AgentOutput for a simple greeting."""
    mock_prompt = "Hello, how can you help me?"
    with agent.override(model=TestModel(call_tools=[])):
        result = await agent.run(mock_prompt, deps=mock_deps)

    assert isinstance(result.output, AgentOutput)
    assert isinstance(result.output.support_response, str)
    assert 0 <= result.output.operation_risk_level <= 10
    assert isinstance(result.output.follow_up_actions, list)


async def test_agent_identifies_client_by_phone(
    mock_deps: AgentDeps,
) -> None:
    """Agent correctly identifies a client when given a valid phone number."""
    mock_client = Client(
        name="Alice Smith",
        email="alice@example.com",
        phone=PhoneNumber("+16502530000"),
        cards=[],
    )
    mock_deps.db.get_client.return_value = mock_client

    mock_model = TestModel(
        call_tools=[],
        custom_output_args={
            "support_response": "Client identified as Alice Smith.",
            "operation_risk_level": 0,
            "follow_up_actions": [],
        },
    )
    mock_prompt = "My phone number is +1 650-253-0000. Who am I?"
    with agent.override(model=mock_model):
        result = await agent.run(mock_prompt, deps=mock_deps)

    assert isinstance(result.output, AgentOutput)
    assert result.output.operation_risk_level == 0


async def test_agent_card_deactivation_has_high_risk(mock_deps: AgentDeps):
    """Agent assigns a high risk level when deactivating a card."""
    mock_model = TestModel(
        call_tools=[],
        custom_output_args={
            "support_response": "Card has been deactivated.",
            "operation_risk_level": 8,
            "follow_up_actions": ["Monitor account for suspicious activity"],
        },
    )
    mock_prompt = "Please deactivate my card 2221000000000000."
    with agent.override(model=mock_model):
        result = await agent.run(mock_prompt, deps=mock_deps)

    assert result.output.operation_risk_level >= 5
    assert len(result.output.follow_up_actions) > 0
