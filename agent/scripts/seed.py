import asyncio
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic_extra_types.payment import PaymentCardNumber
from pydantic_extra_types.phone_numbers import PhoneNumber

from agent.core.database.engine import async_session, engine
from agent.models import Card, Client, Transaction

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def seed_clients(session: "AsyncSession") -> None:
    """Save random information about clients of the bank into the database."""
    clients = [
        Client(
            name="Joe Doe",
            email="jd@example.com",
            phone=PhoneNumber("+1 650-253-0000"),
            cards=[
                Card(
                    number=PaymentCardNumber("4222222222222"),
                    balance=Decimal("200.00"),
                    transactions=[
                        Transaction(
                            description="Grocery Store",
                            amount=Decimal("99.99"),
                        ),
                        Transaction(
                            description="Sport Club",
                            amount=Decimal("13.37"),
                        ),
                    ],
                )
            ],
        ),
        Client(
            name="Sarah Doe",
            email="sd@example.com",
            phone=PhoneNumber("+1 650-253-1111"),
            cards=[
                Card(
                    number=PaymentCardNumber("4111111111111111"),
                    balance=Decimal("250.00"),
                    transactions=[
                        Transaction(
                            description="Shopping",
                            amount=Decimal("130.14"),
                        ),
                        Transaction(
                            description="Sport Club",
                            amount=Decimal("11.99"),
                        ),
                    ],
                ),
                Card(
                    number=PaymentCardNumber("6011111111111117"),
                    balance=Decimal("100.00"),
                    transactions=[
                        Transaction(
                            description="AWS Monthly Billing",
                            amount=Decimal("16.48"),
                        ),
                    ],
                ),
            ],
        ),
    ]
    session.add_all(clients)
    await session.commit()


async def main() -> None:
    """Populate the database with random data."""

    # Create database and tables
    async with engine.begin() as conn:
        await conn.run_sync(Client.metadata.create_all)

    # Save random clients data into db
    async with async_session() as session:
        await seed_clients(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
