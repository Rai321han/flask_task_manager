"""
Task Manager Flask Application.

This module implements a Flask-based REST API and web interface for managing tasks.
It provides endpoints for creating, reading, updating, and deleting tasks, as well as
a web interface for viewing and interacting with tasks.

The application uses SQLAlchemy for database operations and Pydantic for data validation.
"""

from logger.logger import setup_logger
import logging
from flask import Flask, request, render_template, jsonify
from db.db import get_db
from db.models import Task, TaskStatus
from datetime import date
from sqlalchemy import select, or_, asc, desc
from validation.validate import TaskSchema
from pydantic import ValidationError

setup_logger()

logging.getLogger("werkzeug").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.get("/api/v1/tasks/<int:id>")
def show_task(id):
    """Retrieve a single task by its ID.
    
    Args:
        id (int): The unique identifier of the task.
    
    Returns:
        dict: Task data as a dictionary, or error response with 404 status if not found.
    """
    with get_db() as db:
        stmt = select(Task).where(Task.id == id)
        task = db.execute(stmt).scalar_one_or_none()
        if not task:
            logger.error("Task not found | id=%s", id)
            return {"error": "Task not found"}, 404
        return task_to_dict(task)


@app.get("/api/v1/tasks")
def alltasks():
    """Retrieve all tasks with optional filtering and sorting.
    
    Query Parameters:
        q (str): Search query to filter tasks by title or description.
        status (str): Filter tasks by status.
        sort (str): Field to sort by (default: 'created_at').
        order (str): Sort order 'asc' or 'desc' (default: 'asc').
    
    Returns:
        list: List of task dictionaries matching the criteria.
    """
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
                logger.error("Invalid task status")
                return "Invalid status", 400

        sort_column = Task.created_at if sort_by == "created_at" else Task.due_date
        stmt = stmt.order_by(desc(sort_column) if order == "desc" else asc(sort_column))

        tasks = db.execute(stmt).scalars().all()
        logger.info("Tasks fetch successfully")
        return [task_to_dict(t) for t in tasks]


@app.post("/api/v1/tasks")
def create_task():
    """Create a new task.
    
    Request JSON Body:
        title (str): Task title.
        description (str): Task description.
        status (str): Task status.
        due_date (str, optional): Due date in ISO format.
    
    Returns:
        tuple: Task data dictionary and 201 status code on success,
               or error response with 400 status code on validation failure.
    """
    try:
        validated = TaskSchema(**request.get_json())
    except ValidationError as e:
        logger.warning(
            "Validation error while creating task: %s", e.errors()[0].get("msg")
        )
        return jsonify({"errors": e.errors()[0].get("msg")}), 400

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

    logger.info("Task created successfully | id=%s | title=%s", task.id, task.title)

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
    """Update an existing task.
    
    Args:
        task_id (int): The unique identifier of the task to update.
    
    Request JSON Body:
        title (str, optional): Updated task title.
        description (str, optional): Updated task description.
        status (str, optional): Updated task status.
        due_date (str, optional): Updated due date in ISO format.
    
    Returns:
        tuple: Updated task data dictionary and 200 status code on success,
               or error response with 400/404 status code on failure.
    """
    data = request.get_json()

    if not data:
        logger.error("Updating tasks | No data provided")
        return {"error": "no data provided"}, 400

    with get_db() as db:
        task = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()

        if not task:
            logger.error("task not found for id = %s", task_id)
            return {"error": f"task not found"}, 400

        if "title" in data:
            task.title = data["title"]

        if "description" in data:
            task.description = data["description"]

        if "status" in data:
            try:
                task.status = TaskStatus(data["status"])
            except ValueError:
                logger.error("Update task failed | id=%s", task_id)
                return {"error": f"invalid status"}, 400

        if "due_date" in data:
            task.due_date = (
                date.fromisoformat(data["due_date"]) if data["due_date"] else None
            )

        logger.info("Task updated successfully | id=%s", task_id)
        db.commit()
        db.refresh(task)

    return task_to_dict(task), 200


def task_to_dict(task: Task):
    """Convert a Task object to a dictionary.
    
    Args:
        task (Task): The Task object to convert.
    
    Returns:
        dict: Dictionary representation of the task with all fields
              including id, title, description, status, created_at, and due_date.
    """
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "created_at": task.created_at.isoformat(),
        "due_date": task.due_date.isoformat() if task.due_date else None,
    }


@app.delete("/api/v1/tasks/<int:id>")
def delete_task(id):
    """Delete a task by its ID.
    
    Args:
        id (int): The unique identifier of the task to delete.
    
    Returns:
        tuple: Success message and 200 status code on successful deletion,
               or error response with 404 status code if task not found.
    """
    with get_db() as db:
        task = db.execute(select(Task).where(Task.id == id)).scalar_one_or_none()

        if not task:
            logger.error("deletion; non existing id =%s", id)
            return {"error": "Non-existing id"}, 404

        db.delete(task)
        db.commit()
    logger.info("Task created successfully | id=%s", id)
    return {"message": "Task deleted"}, 200


# Frontend routes
@app.get("/")
def home():
    """Render the home page.
    
    Returns:
        str: Rendered HTML template for the home/index page.
    """
    return render_template("task/index.html")


@app.get("/tasks")
def tasks():
    """Render the tasks list page with all tasks.
    
    Returns:
        str: Rendered HTML template displaying all tasks.
    """
    with get_db() as db:
        stmt = select(Task)
        tasks = db.execute(stmt).scalars().all()
    return render_template("task/tasks_list.html", tasks=tasks)
