from datetime import datetime

from sqlmodel import Field, SQLModel

from agent.core.database.utils import get_current_datetime_utc


class AutoIncrementIDMixin(SQLModel):
    """Mixin to provide autoincrement id attribute to be a primary key of the model."""

    id: int | None = Field(
        default=None,
        description="Unique identifier of the user in the database",
        primary_key=True,
    )


class CurrentTimeStampMixin(SQLModel):
    """Mixin to provide creation and update timestamps of the model's record."""

    created_at: datetime = Field(
        description="Automatically set date and time of the creation of the record",
        default_factory=get_current_datetime_utc,
    )
    updated_at: datetime = Field(
        default_factory=get_current_datetime_utc,
        description="Automatically set date and time of the update of the record",
        sa_column_kwargs={"onupdate": get_current_datetime_utc},
    )
