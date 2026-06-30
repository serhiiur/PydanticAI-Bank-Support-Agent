from decimal import Decimal

from pydantic_ai import FunctionToolset, RunContext
from pydantic_extra_types.currency_code import Currency
from pydantic_extra_types.payment import PaymentCardNumber
from pydantic_extra_types.phone_numbers import PhoneNumber

from agent.core.tools import BaseBankAgentToolset
from agent.dependencies import AgentDeps
from agent.exceptions import ClientNotFound
from agent.models import Transaction

card_toolset = FunctionToolset[AgentDeps](
    require_parameter_descriptions=True,
    instructions=(
        "Use this toolset when the client asks to perform some operations with one's bank card."
        "Provide short and concise answers."
    ),
)
currency_toolset = FunctionToolset[AgentDeps](
    require_parameter_descriptions=True,
    instructions=(
        "Use this toolset when the client asks to perform some operations with currencies"
        "such as exchange rates."
    ),
)


@currency_toolset.tool
async def get_currency_exchange_rate(
    ctx: RunContext[AgentDeps],
    from_currency: Currency,
    to_currency: Currency,
) -> Decimal:
    """Return exchange rate from and to the specified currencies.

    :param ctx: Agent's context providing access to the agent's dependencies
    :param from_currency: original currency
    :param to_currency: desired currency
    :return: exchange rate for the given currency
    """
    return await ctx.deps.currency.get_exchange_rate(from_currency, to_currency)


@card_toolset.tool
async def identify_client(
    ctx: RunContext[AgentDeps],
    phone_number: str,
) -> str:
    """Identify the client by their phone number.

    Must be called before any other card operations.

    :param ctx: Agent's context providing access to the agent's dependencies
    :param phone_number: client's phone number provided by the client
    :return: confirmation message with the client's name
    """
    try:
        ctx.deps.db.phone_number = PhoneNumber(phone_number)
    except Exception:
        raise ClientNotFound(
            "Invalid phone number format. Please provide a valid phone number (e.g. +1 650-253-0000)."
        )
    client = await ctx.deps.db.get_client()
    return f"Client identified as {client.name}."


@card_toolset.tool
async def get_client_cards_activity_status(
    ctx: RunContext[AgentDeps],
) -> dict[PaymentCardNumber, bool]:
    """Return activity status of all client's cards in the bank.

    :param ctx: Agent's context providing access to the agent's dependencies
    :return: activity status of all client's cards
    """
    return await ctx.deps.db.get_client_cards_statuses()


@card_toolset.tool
async def get_card_balance(
    ctx: RunContext[AgentDeps],
    card_number: PaymentCardNumber,
) -> Decimal:
    """Return current balance on the client's card.

    :param ctx: Agent's context providing access to the agent's dependencies
    :param card_number: client's card number in the bank
    :return: balance on the client's card
    """
    return await ctx.deps.db.get_client_card_balance(card_number)


@card_toolset.tool
async def get_card_transactions(
    ctx: RunContext[AgentDeps],
    card_number: PaymentCardNumber,
    limit: int = 5,
) -> list[Transaction]:
    """Return latest N (limit argument) transactions from the client's card.

    :param ctx: Agent's context providing access to the agent's dependencies
    :param card_number: client's card number in the bank
    :param limit: number of transactions from the card to return
    :return: latest transactions from the client's card
    """
    return await ctx.deps.db.get_card_transactions(card_number, limit)


@card_toolset.tool
async def deactivate_card(
    ctx: RunContext[AgentDeps],
    card_number: PaymentCardNumber,
) -> bool:
    """Deactivate the client's card in the bank.

    Only use this when there is a security concern or the card is reported lost/stolen.

    :param ctx: Agent's context providing access to the agent's dependencies
    :param card_number: client's card number in the bank
    :return: Positive result of the card deactivation operation
    """
    return await ctx.deps.db.deactivate_card(card_number)


bank_toolsets = [
    BaseBankAgentToolset(currency_toolset),  # ty:ignore[invalid-argument-type]
    BaseBankAgentToolset(card_toolset),  # ty:ignore[invalid-argument-type]
]
