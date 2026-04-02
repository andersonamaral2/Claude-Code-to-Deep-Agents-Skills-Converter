---
name: python-fastapi-todo-app
description: "Creates a simple Todo API with FastAPI, SQLite, and basic CRUD operations."
metadata:
  converted-from: claude-code
  converter-version: "2.0"
  deep-agents-compat: ">=0.0.34"
---

# Python FastAPI Todo App

Creates a simple Todo API with FastAPI, SQLite, and basic CRUD operations.

## Execution Context

This skill runs inside **Deep Agents CLI** (v0.0.34+). Available tools:

| Tool | Usage in this skill |
|------|---------------------|
| `write_file` | Create project files (database.py, models.py, main.py, .env, .gitignore) |
| `execute` | Run shell commands (install deps, start server, run tests) |
| `read_file` | Read created files to verify content |
| `write_todos` | Track execution plan progress |
| `http_request` | Test API endpoints after server starts |

**Critical execution rules:**
1. Always start by creating the plan via `write_todos`.
2. Create files one by one via `write_file` — never try to generate everything at once.
3. Test each module via `execute` immediately after creating it.
4. Use `task` to delegate long or parallel subtasks to sub-agents.

## Execution Plan (use with `write_todos`)

When receiving the request, run `write_todos` with:

- [ ] 1. Verify Python 3.11+ is installed
- [ ] 2. Create project directory and virtual environment
- [ ] 3. Install dependencies (fastapi, uvicorn, sqlalchemy)
- [ ] 4. Create database module (app/database.py)
- [ ] 5. Create models module (app/models.py)
- [ ] 6. Create FastAPI application (app/main.py)
- [ ] 7. Create .env and .gitignore files
- [ ] 8. Start server and test all CRUD endpoints
- [ ] 9. Run smoke tests for all endpoints

## When to Use

Use this skill when the user asks to:
- Create a todo app
- Build a task manager API
- Create a simple REST API with Python and FastAPI

## Prerequisites Check

Before creating any files, use `execute` to verify:

```bash
# Check Python version
python3 --version || { echo "ERROR: Python 3 not found"; exit 1; }

# Verify Python 3.11+
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $PYTHON_VERSION"

# Check pip is available
python3 -m pip --version || { echo "ERROR: pip not found"; exit 1; }
```

If Python is not installed, use `execute` to install:

```bash
# On macOS:
brew install python@3.11

# On Linux:
sudo apt-get update && sudo apt-get install -y python3.11 python3.11-venv
```

## Steps

### 1. Setup Environment

Use `execute` to create the project directory and virtual environment:

```bash
mkdir -p todo-api/app
cd todo-api
python3 -m venv venv
source venv/bin/activate
```

Use `execute` to install dependencies:

```bash
cd todo-api && source venv/bin/activate
pip install fastapi uvicorn sqlalchemy
```

Test via `execute`:

```bash
cd todo-api && source venv/bin/activate
python3 -c "import fastapi; import uvicorn; import sqlalchemy; print('All dependencies OK')"
```

### 2. Create Database Module

Use `write_file` to create `todo-api/app/__init__.py`:

```python
```

Use `write_file` to create `todo-api/app/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./todos.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

Test via `execute`:

```bash
cd todo-api && source venv/bin/activate
python3 -c "from app.database import engine, SessionLocal, Base; print('database module OK')"
```

### 3. Create Models

Use `write_file` to create `todo-api/app/models.py`:

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

Test via `execute`:

```bash
cd todo-api && source venv/bin/activate
python3 -c "from app.models import Todo; print(f'Model OK: {Todo.__tablename__}')"
```

### 4. Create FastAPI Application

Use `write_file` to create `todo-api/app/main.py`:

```python
import os
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from .database import SessionLocal, engine
from .models import Todo as TodoModel, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TodoCreate(BaseModel):
    title: str
    description: str = ""
    completed: bool = False

class TodoUpdate(BaseModel):
    title: str = None
    description: str = None
    completed: bool = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

    class Config:
        from_attributes = True

@app.get("/todos", response_model=List[TodoResponse])
def list_todos(db: Session = Depends(get_db)):
    return db.query(TodoModel).all()

@app.post("/todos", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = TodoModel(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    update_data = todo.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_todo, key, value)
    
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host=host, port=port)
```

Test via `execute`:

```bash
cd todo-api && source venv/bin/activate
python3 -c "from app.main import app; print(f'FastAPI app OK: {len(app.routes)} routes')"
```

### 5. Environment Setup

Before execution, verify required environment variables via `execute`:

```bash
# Check optional variables (with defaults)
echo "API_HOST=${API_HOST:-0.0.0.0} (default: 0.0.0.0)"
echo "API_PORT=${API_PORT:-8000} (default: 8000)"
```

Use `write_file` to create `todo-api/.env`:

```
API_HOST=0.0.0.0
API_PORT=8000
```

Use `write_file` to create `todo-api/.gitignore`:

```
venv/
__pycache__/
*.pyc
*.db
.env
```

### 6. Add Project Notes

Use `write_file` to create `todo-api/AGENTS.md`:

```markdown
# Todo API — Project Notes

- Framework: FastAPI with SQLAlchemy ORM
- Database: SQLite (file: todos.db)
- No authentication required
- Environment: API_HOST, API_PORT configurable via .env
- Endpoints: GET/POST /todos, PUT/DELETE /todos/{id}
```

### 7. Test the API

Use `execute` to start the server in the background:

```bash
cd todo-api && source venv/bin/activate
nohup python3 -m app.main > server.log 2>&1 &
echo $! > server.pid
sleep 2
echo "Server PID: $(cat server.pid)"
```

Use `execute` to run smoke tests on all endpoints:

```bash
echo "=== Testing GET /todos ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/todos
echo ""

echo "=== Testing POST /todos ==="
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk", "completed": false}'
echo ""

echo "=== Testing PUT /todos/1 ==="
curl -s -o /dev/null -w "%{http_code}" -X PUT http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
echo ""

echo "=== Testing DELETE /todos/1 ==="
curl -s -o /dev/null -w "%{http_code}" -X DELETE http://localhost:8000/todos/1
echo ""

echo "=== All smoke tests complete ==="
```

Use `execute` to stop the test server:

```bash
cd todo-api && kill $(cat server.pid) 2>/dev/null; rm -f server.pid
```

## Notes

- Keep it simple, no authentication required
- Uses SQLite to avoid external database dependencies
- Follows FastAPI best practices with Pydantic models
- Supports configuration via environment variables

## Usage with Deep Agents CLI

### Mode 1 — Build (one-shot)
```bash
deepagents -y "Create a Python FastAPI Todo App following the python-fastapi-todo-app skill"
```

### Mode 2 — Interactive
```bash
deepagents
> Create a todo API with FastAPI and SQLite
```

### Mode 3 — Non-interactive (CI/CD)
```bash
deepagents -n -y -S "pip,python3,curl,mkdir" "Create a FastAPI todo app with CRUD endpoints"
```

## Troubleshooting

### Python not found
```bash
# Check:
python3 --version
# Install (macOS):
brew install python@3.11
# Install (Linux):
sudo apt-get install python3.11
```

### pip install fails
```bash
# Ensure venv is activated:
source venv/bin/activate
# Upgrade pip:
python3 -m pip install --upgrade pip
# Retry:
pip install fastapi uvicorn sqlalchemy
```

### Environment variable not set
```bash
# Check what's set:
env | grep API_
# Set manually:
export API_HOST="0.0.0.0"
export API_PORT=8000
# Or load from .env:
set -a && source .env && set +a
```

### Server won't start
```bash
# Check if port is in use:
lsof -i :8000
# Check server logs:
cat server.log
# Try a different port:
export API_PORT=8001
```

### Context window overflow
```
Use /compact to force compaction before continuing.
Consider splitting the task with `task` sub-agents.
```
