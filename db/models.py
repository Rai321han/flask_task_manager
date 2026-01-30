from datetime import datetime, date, timezone
from sqlalchemy import String, DateTime, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column
from db.db import Base
import enum


class TaskStatus(enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class Task(Base):
    __tablename__ = "tasks"

    # id (int, auto increment)
    id: Mapped[int] = mapped_column(primary_key=True)

    # title (string, required)
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    # description (string, optional)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    # status (todo, in_progress, done)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        default=TaskStatus.todo,
        nullable=False,
    )

    # created_at (ISO datetime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        nullable=False,
    )

    # due_date (optional: YYYY-MM-DD)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
