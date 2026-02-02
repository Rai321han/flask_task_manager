from pydantic import BaseModel, field_validator, Field, model_validator
from pydantic_core import PydanticCustomError
from typing import Optional
from datetime import date
from db.models import TaskStatus


class TaskSchema(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str]
    status: Optional[str] = TaskStatus.todo.value
    due_date: Optional[date]

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
