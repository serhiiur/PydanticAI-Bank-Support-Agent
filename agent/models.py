from decimal import Decimal

from pydantic import EmailStr
from pydantic_extra_types.payment import PaymentCardNumber
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlmodel import Field, Relationship

from agent.core.database.mixins import AutoIncrementIDMixin, CurrentTimeStampMixin


class Client(AutoIncrementIDMixin, CurrentTimeStampMixin, table=True):
    """Database model to represent a client."""

    name: str = Field(
        description="Name of the client",
    )
    email: EmailStr = Field(
        description="Email of the client",
        unique=True,
    )
    phone: PhoneNumber = Field(
        description="Phone number of the client",
        schema_extra={"examples": "+1 650-253-0000"},
        unique=True,
        index=True,
    )
    cards: list["Card"] = Relationship(
        back_populates="client",
        cascade_delete=True,
        sa_relationship_kwargs={"lazy": "joined"},
    )


class Card(AutoIncrementIDMixin, CurrentTimeStampMixin, table=True):
    """Database model to represent a client's card."""

    number: PaymentCardNumber = Field(
        description="Number of the card",
        schema_extra={"examples": "2221000000000000"},
    )
    balance: Decimal = Field(
        description="Current balance on the card",
        max_digits=10,
        decimal_places=2,
        gt=0,
    )
    is_active: bool = Field(
        default=True,
        description="Whether the card is active or not",
    )
    client_id: int | None = Field(
        description="Reference to the card",
        default=None,
        foreign_key="client.id",
    )
    client: "Client" = Relationship(back_populates="cards")
    transactions: list["Transaction"] = Relationship(
        back_populates="card",
        cascade_delete=True,
        sa_relationship_kwargs={
            "lazy": "joined",
            "order_by": "Card.created_at",
        },
    )


class Transaction(AutoIncrementIDMixin, CurrentTimeStampMixin, table=True):
    """Database model to represent a transaction from the client's bank account."""

    description: str = Field(
        description="Description to describe the transaction",
        min_length=0,
        max_length=255,
    )
    amount: Decimal = Field(
        description="Amount of money spent during the transaction",
        max_digits=10,
        decimal_places=2,
        gt=0,
    )
    card_id: int | None = Field(
        description="Reference to the card",
        default=None,
        foreign_key="card.id",
    )
    card: "Card" = Relationship(back_populates="transactions")
