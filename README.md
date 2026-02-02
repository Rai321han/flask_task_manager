# Task Manager Application

A Flask-based REST API and web interface for managing tasks with SQLAlchemy ORM and Pydantic validation.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
  - [Base URL](#base-url)
  - [Endpoints](#endpoints)
  - [Request/Response Examples](#requestresponse-examples)
  - [Status Codes](#status-codes)
- [Frontend Routes](#frontend-routes)
- [Database Schema](#database-schema)
- [Technologies Used](#technologies-used)

---

## Overview

The Task Manager Application is a full-stack web application that allows users to create, read, update, and delete (CRUD) tasks. It features:

- RESTful API for programmatic task management
- Web interface for browsing and interacting with tasks
- Task filtering, searching, and sorting capabilities
- Data validation using Pydantic
- SQLite database for persistent storage
- Comprehensive logging

---

## Project Structure

```
task_manager/
├── app.py                    # Main Flask application with API routes
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (DATABASE_URL, FLASK_ENV)
├── README.md                 # This file
│
├── db/                       # Database layer
│   ├── db.py                 # Database engine and session management
│   ├── models.py             # SQLAlchemy ORM models (Task, TaskStatus)
│   └── init_db.py            # Database initialization script
│
├── logger/                   # Logging configuration
│   └── logger.py             # Logger setup
│
├── validation/               # Input validation
│   └── validate.py           # Pydantic schema for task validation
│
├── static/                   # Static assets
│   └── style.css             # CSS styling
│
├── templates/                # HTML templates
│   └── task/
│       ├── base.html         # Base template
│       ├── index.html        # Home page template
│       └── tasks_list.html   # Tasks list template
│
└── logs/                     # Application logs directory (generated)

```

---

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Steps

1. **Clone or navigate to the project directory:**
   ```bash
   cd task_manager
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database:**
   ```bash
   python db/init_db.py
   ```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=sqlite:///task_manager.db
```

**Variables:**
- `FLASK_APP`: Entry point for Flask application
- `FLASK_ENV`: Environment mode (development/production)
- `DATABASE_URL`: Database connection string (SQLite by default)

---

## Running the Application

Start the Flask development server:

```bash
flask run
```

The application will be available at:
- **API Base URL:** `http://localhost:5000/api/v1`
- **Web Interface:** `http://localhost:5000`

---

## API Documentation

### Base URL

```
http://localhost:5000/api/v1
```

### Endpoints

#### 1. **Get All Tasks**

**Request:**
```
GET /api/v1/tasks
```

**Query Parameters:**
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `q` | string | Search query (filters by title or description) | - |
| `status` | string | Filter by status (todo, in_progress, done) | - |
| `sort` | string | Sort field (created_at or due_date) | created_at |
| `order` | string | Sort order (asc or desc) | asc |

**Example:**
```http
GET /api/v1/tasks?q=project&status=todo&sort=due_date&order=desc
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Complete project",
    "description": "Finish the task manager project",
    "status": "in_progress",
    "created_at": "2026-02-01T10:30:00",
    "due_date": "2026-02-15"
  }
]
```

---

#### 2. **Get Single Task**

**Request:**
```http
GET /api/v1/tasks/<id>
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Task ID (required, in URL) |

**Example:**
```http
GET /api/v1/tasks/1
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Complete project",
  "description": "Finish the task manager project",
  "status": "in_progress",
  "created_at": "2026-02-01T10:30:00",
  "due_date": "2026-02-15"
}
```

**Response (404 Not Found):**
```json
{
  "error": "Task not found"
}
```

---

#### 3. **Create Task**

**Request:**
```http
POST /api/v1/tasks
Content-Type: application/json
```

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Task title (min 1 character) |
| `description` | string | No | Task description |
| `status` | string | No | Task status (default: todo) |
| `due_date` | string | No | Due date in ISO format (YYYY-MM-DD) |

**Example:**
```bash
curl -X POST http://localhost:5000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Buy milk, eggs, and bread",
    "status": "todo",
    "due_date": "2026-02-10"
  }'
```

**Response (201 Created):**
```json
{
  "id": 2,
  "title": "Buy groceries",
  "description": "Buy milk, eggs, and bread",
  "status": "todo",
  "created_at": "2026-02-02T14:20:00",
  "due_date": "2026-02-10"
}
```

**Response (400 Bad Request):**
```json
{
  "errors": "missing title"
}
```

---

#### 4. **Update Task**

**Request:**
```http
PATCH /api/v1/tasks/<id>
Content-Type: application/json
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Task ID (required, in URL) |

**Request Body (all fields optional):**
| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Updated task title |
| `description` | string | Updated task description |
| `status` | string | Updated status (todo, in_progress, done) |
| `due_date` | string | Updated due date (YYYY-MM-DD) or null |

**Example:**
```bash
curl -X PATCH http://localhost:5000/api/v1/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "done",
    "due_date": "2026-02-05"
  }'
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Complete project",
  "description": "Finish the task manager project",
  "status": "done",
  "created_at": "2026-02-01T10:30:00",
  "due_date": "2026-02-05"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "no data provided"
}
```

---

#### 5. **Delete Task**

**Request:**
```http
DELETE /api/v1/tasks/<id>
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Task ID (required, in URL) |

**Example:**
```bash
curl -X DELETE http://localhost:5000/api/v1/tasks/1
```

**Response (200 OK):**
```json
{
  "message": "Task deleted"
}
```

**Response (404 Not Found):**
```json
{
  "error": "Non-existing id"
}
```

---

### Request/Response Examples

**Create Multiple Tasks:**
```bash
# Task 1
curl -X POST http://localhost:5000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Flask","status":"in_progress"}'

# Task 2
curl -X POST http://localhost:5000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Review code","due_date":"2026-02-03"}'
```

**Filter Tasks:**
```bash
# Get all "todo" tasks
curl "http://localhost:5000/api/v1/tasks?status=todo"

# Search for tasks with "project" in title/description
curl "http://localhost:5000/api/v1/tasks?q=project"

# Get tasks sorted by due date descending
curl "http://localhost:5000/api/v1/tasks?sort=due_date&order=desc"
```

---

### Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input or missing data |
| 404 | Not Found | Task not found |

---

## Frontend Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home/index page |
| `/tasks` | GET | Tasks list page with all tasks |

**Example:**
```
http://localhost:5000/          # Home page
http://localhost:5000/tasks     # All tasks view
```

---

## Technologies Used

| Technology | Purpose |
|-----------|---------|
| Flask 3.1.2 | Web framework for REST API and web interface |
| SQLAlchemy 2.0.46 | ORM for database operations |
| Pydantic | Data validation and schema definition |
| SQLite | Lightweight embedded database |
| Python-dotenv | Environment variable management |
| Werkzeug | WSGI utility library |
| Jinja2 | Template engine for HTML rendering |

---

## Notes

- All timestamps are stored in UTC and returned in ISO 8601 format
- Task titles are required and must contain at least 1 character
- Status values are case-sensitive
- Due dates should be provided in YYYY-MM-DD format
- The database is automatically initialized on first run
- Logging is configured to track all major operations and errors
