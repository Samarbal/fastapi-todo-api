from typing import List

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field, field_validator

app = FastAPI(
    title="To-Do List CRUD API",
    version="1.0.0",
    description="""
A production-style To-Do List API built with **FastAPI**.

### Features
- In-memory task storage
- Full CRUD operations
- Input validation
- Proper HTTP status codes
- Interactive Swagger documentation
""",
)

# ==========================================================
# Pydantic Models
# ==========================================================

class Task(BaseModel):
    """Represents a task stored in the system."""

    id: int
    title: str
    done: bool


class TaskCreate(BaseModel):
    """Request model for creating a new task."""

    title: str = Field(..., example="Learn FastAPI")

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str):
        if not value.strip():
            raise ValueError("Title cannot be empty or whitespace.")
        return value.strip()


class TaskUpdate(BaseModel):
    """Request model for updating an existing task."""

    title: str = Field(..., example="Master FastAPI")
    done: bool

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str):
        if not value.strip():
            raise ValueError("Title cannot be empty or whitespace.")
        return value.strip()


# ==========================================================
# In-Memory Database
# ==========================================================

tasks: List[Task] = [
    Task(id=1, title="Learn FastAPI", done=False),
    Task(id=2, title="Build CRUD API", done=True),
    Task(id=3, title="Read API Documentation", done=False),
]


# ==========================================================
# Helper Function
# ==========================================================

def get_task_by_id(task_id: int) -> Task:
    """
    Find a task by ID.

    Raises:
        HTTPException(404): If task does not exist.
    """
    for task in tasks:
        if task.id == task_id:
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with ID {task_id} was not found.",
    )


# ==========================================================
# API Endpoints
# ==========================================================

@app.get(
    "/",
    summary="API Information",
    description="Returns basic information and metadata about the To-Do API.",
)
def root():
    return {
        "name": "To-Do List CRUD API",
        "version": "1.0.0",
        "status": "Running",
    }


@app.get(
    "/health",
    summary="Health Check",
    description="Checks whether the API service is healthy and operational.",
)
def health():
    return {
        "status": "healthy"
    }


@app.get(
    "/tasks",
    response_model=List[Task],
    summary="Get All Tasks",
    description="Returns the complete list of tasks currently stored in memory.",
)
def get_tasks():
    return tasks


@app.get(
    "/tasks/{task_id}",
    response_model=Task,
    summary="Get Task By ID",
    description="Returns a single task using its unique identifier.",
)
def get_task(task_id: int):
    return get_task_by_id(task_id)


@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Task",
    description="""
Creates a new task.

Validation:
- Title cannot be empty.
- Title cannot contain only whitespace.

Returns **201 Created** upon success.
""",
)
def create_task(task: TaskCreate):
    new_task = Task(
        id=max((t.id for t in tasks), default=0) + 1,
        title=task.title,
        done=False,
    )

    tasks.append(new_task)
    return new_task


@app.put(
    "/tasks/{task_id}",
    response_model=Task,
    summary="Update Existing Task",
    description="""
Updates both the title and completion status of an existing task.

Validation:
- Title cannot be empty.
- Title cannot contain only whitespace.

Returns **404** if the task does not exist.
""",
)
def update_task(task_id: int, updated_task: TaskUpdate):
    task = get_task_by_id(task_id)

    task.title = updated_task.title
    task.done = updated_task.done

    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Task",
    description="""
Deletes a task by its ID.

Returns:
- **204 No Content** if deletion succeeds.
- **404 Not Found** if the task does not exist.
""",
)
def delete_task(task_id: int):
    task = get_task_by_id(task_id)
    tasks.remove(task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==========================================================
# Custom Validation Error Handler
# ==========================================================

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """
    Converts Pydantic validation errors into HTTP 400
    instead of FastAPI's default 422.
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": exc.errors()
        },
    )