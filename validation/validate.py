from pydantic import BaseModel, field_validator, Field
from typing import Optional
from datetime import date
from db.models import TaskStatus


class TaskSchema(BaseModel):
    title: str = Field(..., min_length=1, description="Title is required")
    description: Optional[str]
    status: Optional[str] = TaskStatus.todo.value
    due_date: Optional[date]

    @field_validator("status")
    def check_status(cls, v):
        allowed = [s.value for s in TaskStatus]
        if v not in allowed:
            print("here")
            raise ValueError(f"Invalid status. Must be one of {allowed}")
        return v
