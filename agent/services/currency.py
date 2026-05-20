from decimal import Decimal
from urllib.parse import urljoin

from httpx import AsyncClient
from pydantic import HttpUrl
from pydantic_extra_types.currency_code import Currency

from agent.exceptions import CurrencyExchangeRateNotFound


class CurrencyService:
    """Service to perform operations with currencies such as exchange rates."""

    def __init__(self, api_url: HttpUrl, http_client: AsyncClient) -> None:
        """Initialize class objects.

        :param api_url: URL to the API to fetch exchange rates from
        :param http_client: HTTP client to interact with the currency API
        """
        self.api_url = str(api_url)
        self.http_client = http_client

    async def get_exchange_rate(
        self,
        from_currency: Currency,
        to_currency: Currency,
    ) -> Decimal:
        """Return exchange rate from one currency to another.

        :param from_currency: source currency
        :param to_currency: desired currency
        :raises CurrencyExchangeRateNotFound: if exchange rate can't be returned
        :return: exchange rate for the specified currency
        """
        url = urljoin(self.api_url, from_currency)
        resp = await self.http_client.get(url)
        try:
            exchange_rate = resp.json()["conversion_rates"][to_currency]
        except KeyError:
            raise CurrencyExchangeRateNotFound
        return Decimal(str(exchange_rate))
