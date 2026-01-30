from flask import Flask, request
from db.db import get_db
from db.models import Task, TaskStatus
from datetime import date
from sqlalchemy import select, insert
from dotenv import load_dotenv


app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, World!"


@app.get("/api/v1/tasks")
def alltasks():
    with get_db() as db:
        stmt = select(Task)
        tasks = db.execute(stmt).scalars().all()
        return tasks


@app.get("/api/v1/tasks/<int:id>")
def show_task(id):
    with get_db() as db:
        stmt = select(Task).where(Task.id == id)
        task = db.execute(stmt)
        return task


@app.post("/api/v1/tasks")
def create_task():
    data = request.get_json()

    stmt = (
        insert(Task)
        .values(
            title=data["title"],
            description=data.get("description"),
            status=TaskStatus(data["status"]),
            due_date=(
                date.fromisoformat(data["due_date"]) if data.get("due_date") else None
            ),
        )
        .returning(Task)
    )

    with get_db() as db:
        task = db.execute(stmt).scalar_one()
        db.commit()

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "created_at": task.created_at.isoformat(),
        "due_date": task.due_date.isoformat() if task.due_date else None,
    }, 201
