from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic_extra_types.payment import PaymentCardNumber
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlmodel import select

from agent.exceptions import ClientCardNotFound, ClientNotFound
from agent.models import Card, Client, Transaction

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class BankDatabaseService:
    """Service to represent the database of the bank."""

    def __init__(self, session: "AsyncSession", phone_number: PhoneNumber) -> None:
        """Initialize the class attributes.

        :param session: database session object
        :param phone_number: phone number of the client
        """
        self.session = session
        self.phone_number = phone_number

    async def get_client(self) -> Client:
        """Identify client by the phone number.

        :raises ClientNotFound: unless such client exists in the bank database
        :return: information about client from the database
        """
        stmt = select(Client).where(Client.phone == self.phone_number)
        if client := (await self.session.execute(stmt)).scalar():
            return client
        raise ClientNotFound("No such client in the bank")

    async def get_client_cards(self) -> dict[PaymentCardNumber, Card]:
        """Return information about all client's cards in the bank.

        :return: information about client's cards
        """
        client = await self.get_client()
        return {card.number: card for card in client.cards}

    async def get_client_card(self, card_number: PaymentCardNumber) -> Card:
        """Return information about specific client's card.

        :param card_number: client's card number to get the information about
        :return: information about client's card
        """
        cards = await self.get_client_cards()
        try:
            return cards[card_number]
        except KeyError as e:
            raise ClientCardNotFound("No such card") from e

    async def get_client_cards_statuses(self) -> dict[PaymentCardNumber, bool]:
        """Return activity status of the client's cards.

        :return: activity status of the client's cards
        """
        cards = await self.get_client_cards()
        return {cart_number: card.is_active for cart_number, card in cards.items()}

    async def get_client_card_balance(self, card_number: PaymentCardNumber) -> Decimal:
        """Return the current balance on the specified client's card.

        :param card_number: card to return the balance of
        :return: current balance of the card
        """
        card = await self.get_client_card(card_number)
        return card.balance

    async def get_card_transactions(
        self,
        card_number: PaymentCardNumber,
        limit: int = 5,
    ) -> list[Transaction]:
        """Return information about latest transactions on the client's card.

        :param card_number: card to return latest transactions of
        :param limit: number of transactions for the card to return
        :return: latest transactions on the client's card
        """
        card = await self.get_client_card(card_number)
        return card.transactions[:limit]

    async def deactivate_card(self, card_number: PaymentCardNumber) -> bool:
        """Deactivate the client's card.

        :param card_number: client's card to deactivate
        :return: result of the deactivation operation (true)
        """
        card = await self.get_client_card(card_number)
        card.is_active = False
        self.session.add(card)
        await self.session.commit()
        return True
