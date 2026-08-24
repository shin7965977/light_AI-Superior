from enum import Enum

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    TURN_ON = "TURN_ON"
    TURN_OFF = "TURN_OFF"
    SET_BRIGHTNESS = "SET_BRIGHTNESS"
    CLARIFY = "CLARIFY"
    UNKNOWN = "UNKNOWN"


class BulbContext(BaseModel):
    is_on: bool
    brightness: float = Field(ge=0.0, le=1.0)


class ActionSchema(BaseModel):
    action: ActionType
    value: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Target brightness normalized between 0.0 and 1.0",
    )
    reasoning: str | None = Field(
        default=None,
        description="Explanation of the parsed intent",
    )
    clarification_prompt: str | None = Field(
        default=None,
        description="Question asked to clarify user intent when ambiguous",
    )
    clarification_options: list[str] | None = Field(
        default=None,
        description="List of suggested options for disambiguation",
    )
