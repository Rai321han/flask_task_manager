from pydantic import BaseModel, field_validator, Field, model_validator
from pydantic_core import PydanticCustomError
from typing import Optional
from datetime import date
from db.models import TaskStatus


class TaskSchema(BaseModel):
    title: str = Field(..., min_length=1)
    status: Optional[str] = TaskStatus.todo.value
    due_date: Optional[date] = None
    description: Optional[str] = None

    @field_validator("due_date")
    def validate_due_date(cls, v):
        # Only validate if user provided a value
        if v in (None, ""):
            return None
        # If it's already a date, just return it
        if isinstance(v, date):
            return v
        # Try to parse string into date
        try:
            return date.fromisoformat(v)
        except Exception:
            raise ValueError(
                f"due_date must be a valid date in YYYY-MM-DD format, got {v!r}"
            )

    @model_validator(mode="before")
    def check_title(cls, v):
        if "title" not in v or not v["title"].strip():
            raise PydanticCustomError("missing_title", "missing title")
        return v

    @field_validator("status")
    def check_status(cls, v):
        allowed = [s.value for s in TaskStatus]
        if v not in allowed:
            raise PydanticCustomError("invalid_status", f"invalid status")
        return v


def ValidateStatus(status):
    allowed = [s.value for s in TaskStatus]
    if status not in allowed:
        raise ValueError("invalid status")
    return status
