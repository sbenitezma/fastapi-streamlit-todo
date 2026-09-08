"""Definition of the five task REST endpoints.

Routes only orchestrate: they validate with the Pydantic models, delegate to a
:class:`~api.todos_service.TodoService` (injected with ``Depends``) and let its
domain errors bubble up -- ``api.main`` turns :class:`~api.todos_service.TodoNotFound`
into a 404 and :class:`~api.todos_service.EmptyUpdate` into a 400.
"""

from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query, Request, status

from api.database import Database
from api.models import Status, TodoCreate, TodoRead, TodoStats, TodoUpdate
from api.todos_service import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    TodoRepository,
    TodoService,
)

router = APIRouter(prefix="/api", tags=["todos"])

DateField = Literal["created", "updated", "completed"]


def get_todo_service(request: Request) -> TodoService:
    """Build a service over the app's Database (set on app.state in the lifespan)."""
    db: Database = request.app.state.db
    return TodoService(TodoRepository(db))


@router.get("/todos", response_model=list[TodoRead])
def list_todos(
    status_filter: Status | None = Query(default=None, alias="status"),
    date_field: DateField = Query(
        default="created",
        description="Which timestamp the date range applies to.",
    ),
    date_from: date | None = Query(
        default=None, description="Inclusive lower bound (YYYY-MM-DD)."
    ),
    date_to: date | None = Query(
        default=None, description="Inclusive upper bound (YYYY-MM-DD)."
    ),
    limit: int = Query(
        default=DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description=f"Page size, 1-{MAX_PAGE_SIZE} (default {DEFAULT_PAGE_SIZE}).",
    ),
    offset: int = Query(default=0, ge=0, description="Rows to skip (with limit)."),
    service: TodoService = Depends(get_todo_service),
) -> list[dict]:
    """Return tasks.

    Accepts ``?status=pending|done`` and a date range via ``date_from`` /
    ``date_to`` applied to ``date_field`` (``created``, ``updated`` or
    ``completed``), plus ``limit`` / ``offset`` paging. The result is always
    capped (an unbounded list is a trivial resource-exhaustion vector).
    Malformed dates → 422.
    """
    return service.list_todos(
        status_filter, date_field, date_from, date_to, limit, offset
    )


@router.get("/todos/stats", response_model=TodoStats)
def todo_stats(service: TodoService = Depends(get_todo_service)) -> dict:
    """Total / pending / done counts for the whole table."""
    return service.stats()


@router.get("/todos/{todo_id}", response_model=TodoRead)
def get_todo(todo_id: int, service: TodoService = Depends(get_todo_service)) -> dict:
    """Return the details of a single task."""
    return service.get_todo(todo_id)


@router.post("/todos", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(
    payload: TodoCreate, service: TodoService = Depends(get_todo_service)
) -> dict:
    """Create a new task.

    Title is mandatory; description and a (non-future) ``created_at`` date are
    optional.
    """
    created_at = payload.created_at.isoformat() if payload.created_at else None
    return service.create_todo(payload.title, payload.description, created_at)


@router.patch("/todos/{todo_id}", response_model=TodoRead)
def update_todo(
    todo_id: int,
    changes: TodoUpdate,
    service: TodoService = Depends(get_todo_service),
) -> dict:
    """Update the title, description and/or status of an existing task."""
    return service.update_todo(todo_id, changes.model_dump(exclude_unset=True))


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, service: TodoService = Depends(get_todo_service)) -> None:
    """Delete a task. Returns 404 if it does not exist."""
    service.delete_todo(todo_id)
