from agent.core.exceptions import BaseAgentException


class ClientNotFound(BaseAgentException):
    """Raise when there's no such client in the bank."""


class ClientCardNotFound(BaseAgentException):
    """Raise when the client has no such card in the bank."""


class CurrencyExchangeRateNotFound(BaseAgentException):
    """Raise when the exchange rate for the specified currency not found."""
