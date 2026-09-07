"""Definition of the five task REST endpoints.

Routes only orchestrate: they validate with the Pydantic models, call the helpers
in :mod:`api.database` and turn missing data into clear ``HTTPException`` responses.
"""

from datetime import date
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query, status

from api import database
from api.models import Status, TodoCreate, TodoRead, TodoUpdate

router = APIRouter(prefix="/api", tags=["todos"])

DateField = Literal["created", "updated", "completed"]


@router.get("/todos", response_model=list[TodoRead])
def list_todos(
    status_filter: Optional[Status] = Query(default=None, alias="status"),
    date_field: DateField = Query(
        default="created",
        description="Which timestamp the date range applies to.",
    ),
    date_from: Optional[date] = Query(
        default=None, description="Inclusive lower bound (YYYY-MM-DD)."
    ),
    date_to: Optional[date] = Query(
        default=None, description="Inclusive upper bound (YYYY-MM-DD)."
    ),
) -> list[dict]:
    """Return every task.

    Accepts ``?status=pending|done`` and a date range via ``date_from`` /
    ``date_to`` applied to ``date_field`` (``created``, ``updated`` or
    ``completed``). Malformed dates are rejected with 422.
    """
    return database.list_todos(
        status_filter,
        date_field,
        date_from.isoformat() if date_from else None,
        date_to.isoformat() if date_to else None,
    )


@router.get("/todos/{todo_id}", response_model=TodoRead)
def get_todo(todo_id: int) -> dict:
    """Return the details of a single task."""
    todo = database.get_todo(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail=f"No task with id {todo_id}")
    return todo


@router.post("/todos", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate) -> dict:
    """Create a new task.

    Title is mandatory; description and a (non-future) ``created_at`` date are
    optional.
    """
    created_at = payload.created_at.isoformat() if payload.created_at else None
    return database.create_todo(payload.title, payload.description, created_at)


@router.patch("/todos/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: int, changes: TodoUpdate) -> dict:
    """Update the title, description and/or status of an existing task."""
    fields = changes.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(
            status_code=400,
            detail="Send at least one field: title, description or status",
        )

    updated = database.update_todo(todo_id, fields)
    if updated is None:
        raise HTTPException(status_code=404, detail=f"No task with id {todo_id}")
    return updated


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int) -> None:
    """Delete a task. Returns 404 if it does not exist."""
    if not database.delete_todo(todo_id):
        raise HTTPException(status_code=404, detail=f"No task with id {todo_id}")
