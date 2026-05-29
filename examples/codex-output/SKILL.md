---
name: python-fastapi-todo-app
description: "Creates a simple Todo REST API with FastAPI, SQLite, and basic CRUD operations. Use when the user asks to create a todo app, task manager API, or a simple Python REST API with create/read/update/delete endpoints."
metadata:
  converted-from: claude-code
  converter-version: "2.2"
  codex-compat: ">=0.98.0"
---

# Skill: Python FastAPI Todo App

> Creates a simple Todo API with FastAPI, SQLite, and basic CRUD operations.

## When to use

When the user asks to create a todo app, task manager API, or simple REST API with Python.

## Steps

First, make sure Python 3.11+ is installed. On macOS use `brew install python@3.11`, on Linux use `apt-get install python3.11`.

Create the project directory and initialize a virtual environment:

```bash
mkdir -p todo-api/app
cd todo-api
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies:

```bash
pip install fastapi uvicorn sqlalchemy
```

Create the file `app/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./todos.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

Create the file `app/models.py`:

```python
from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, default="")
    completed = Column(Boolean, default=False)
```

Create `app/main.py` with the FastAPI app, including these endpoints:

- `GET /todos` — list all todos
- `POST /todos` — create a new todo
- `PUT /todos/{id}` — update a todo
- `DELETE /todos/{id}` — delete a todo

The app should read `$API_HOST` and `$API_PORT` from the environment for the server bind address.

Add the project conventions to `AGENTS.md` at the root (Codex reads `AGENTS.md` for persistent project context).

Test the API:

```bash
curl http://localhost:8000/todos
```

```bash
curl -X POST http://localhost:8000/todos -H "Content-Type: application/json" -d '{"title": "Buy milk", "completed": false}'
```

For each endpoint, run a quick smoke test to make sure it returns 200.

## Notes

- Keep it simple, no auth needed
- Use SQLite so there's no external database dependency
- Add a `.env` with `API_HOST=0.0.0.0` and `API_PORT=8000`
