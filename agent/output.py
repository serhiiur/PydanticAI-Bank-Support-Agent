from pydantic import BaseModel, Field


class AgentOutput(BaseModel):
    """Output agent schema."""

    support_response: str = Field(
        description="Response of the support agent to the client of the bank",
    )
    operation_risk_level: int = Field(
        description="Risk level of the financial operation performed on the client's bank card",
        ge=0,
        le=10,
    )
    follow_up_actions: list[str] = Field(
        description="List of follow-up actions offered by the support agent to the client",
        default_factory=list,
    )
