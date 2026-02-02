from flask import Flask, request, render_template, redirect, abort, jsonify
from db.db import get_db
from db.models import Task, TaskStatus
from datetime import date
from sqlalchemy import select, update, or_, asc, desc
from validation.validate import TaskSchema
from pydantic import ValidationError

from dotenv import load_dotenv


app = Flask(__name__)


@app.get("/api/v1/tasks/<int:id>")
def show_task(id):
    with get_db() as db:
        stmt = select(Task).where(Task.id == id)
        task = db.execute(stmt).scalar_one_or_none()
        if not task:
            return {"error": "Task not found"}, 404
        return task_to_dict(task)


@app.get("/api/v1/tasks")
def alltasks():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    sort_by = request.args.get("sort", "created_at").strip()
    order = request.args.get("order", "asc").lower()

    with get_db() as db:
        stmt = select(Task)

        if q:
            stmt = stmt.where(
                or_(Task.title.ilike(f"%{q}%"), Task.description.ilike(f"%{q}%"))
            )

        if status:
            try:
                stmt = stmt.where(Task.status == TaskStatus(status))
            except ValueError:
                return "Invalid status", 400

        sort_column = Task.created_at if sort_by == "created_at" else Task.due_date
        stmt = stmt.order_by(desc(sort_column) if order == "desc" else asc(sort_column))

        tasks = db.execute(stmt).scalars().all()
        return [task_to_dict(t) for t in tasks]


@app.post("/api/v1/tasks")
def create_task():
    try:
        validated = TaskSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400

    task = Task(
        title=validated.title,
        description=validated.description,
        status=TaskStatus(validated.status),
        due_date=validated.due_date,
    )

    with get_db() as db:
        db.add(task)
        db.commit()
        db.refresh(task)

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "created_at": task.created_at.isoformat(),
        "due_date": task.due_date.isoformat() if task.due_date else None,
    }, 201


@app.patch("/api/v1/tasks/<int:task_id>")
def update_task(task_id):
    data = request.get_json()

    if not data:
        abort(400, "No data provided")

    with get_db() as db:
        task = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()

        if not task:
            abort(404, "Task not found")

        # 🔹 PATCH only provided fields
        if "title" in data:
            task.title = data["title"]

        if "description" in data:
            task.description = data["description"]

        if "status" in data:
            try:
                task.status = TaskStatus(data["status"])
            except ValueError:
                return {
                    "error": f"Invalid status value, must be one of: {[s.value for s in TaskStatus]}"
                }, 400

        if "due_date" in data:
            task.due_date = (
                date.fromisoformat(data["due_date"]) if data["due_date"] else None
            )

        db.commit()
        db.refresh(task)

    return task_to_dict(task), 200


def task_to_dict(task: Task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "created_at": task.created_at.isoformat(),
        "due_date": task.due_date.isoformat() if task.due_date else None,
    }


@app.post("/tasks/<int:id>/status")
def update_task_status(id):
    new_status = request.form.get("status")

    with get_db() as db:
        stmt = update(Task).where(Task.id == id).values(status=TaskStatus(new_status))
        db.execute(stmt)
        db.commit()

    return redirect(f"/tasks/{id}")


@app.delete("/api/v1/tasks/<int:id>")
def delete_task(id):
    with get_db() as db:
        task = db.execute(select(Task).where(Task.id == id)).scalar_one_or_none()

        if not task:
            return {"error": "Task not found"}, 404

        db.delete(task)
        db.commit()
    return {"message": "Task deleted"}, 200


# frontend route
@app.get("/tasks")
def home():
    with get_db() as db:
        stmt = select(Task)
        tasks = db.execute(stmt).scalars().all()
    return render_template("task/tasks_list.html", tasks=tasks)


@app.get("/tasks/<int:id>")
def task_detail(id):
    with get_db() as db:
        stmt = select(Task).where(Task.id == id)
        task = db.execute(stmt).scalar_one_or_none()

    if not task:
        return "Task not found", 404

    return render_template("task/task_details.html", task=task)
