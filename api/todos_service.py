"""Task persistence and business rules, split into two layers.

* :class:`TodoRepository` -- the **Repository pattern**. The only code that
  speaks SQL for the ``todos`` table. It takes a *connection provider* (so it can
  be pointed at a temp database in tests), always uses parameterized queries and
  returns plain ``dict`` rows.
* :class:`TodoService` -- the business rules the API needs: a task must exist, a
  ``PATCH`` has to change something, ``completed_at`` is derived from status
  transitions. It raises domain errors (:class:`TodoNotFound`,
  :class:`EmptyUpdate`) instead of returning ``None`` / ``False``; ``api.main``
  maps those onto HTTP responses.

Neither layer imports FastAPI, so both can be unit tested on their own.
"""

from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from sqlite3 import Connection

from api import database

# Date columns the list query is allowed to filter on. The mapping doubles as a
# whitelist: only these values can ever reach an SQL string.
DATE_COLUMNS = {
    "created": "created_at",
    "updated": "updated_at",
    "completed": "completed_at",
}

# The list endpoint is always paginated: a missing ``limit`` falls back to
# DEFAULT_PAGE_SIZE and anything larger is clamped to MAX_PAGE_SIZE, so a single
# request can never be asked to materialize the whole table.
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 1000

ConnectionProvider = Callable[[], Connection]


# --------------------------------------------------------------------------- #
# Domain errors
# --------------------------------------------------------------------------- #
class TodoServiceError(Exception):
    """Base class for problems the service reports to its caller."""


class TodoNotFound(TodoServiceError):
    """No task exists with the given id."""

    def __init__(self, todo_id: int) -> None:
        super().__init__(f"No task with id {todo_id}")
        self.todo_id = todo_id


class EmptyUpdate(TodoServiceError):
    """A ``PATCH`` arrived without a single field to change."""

    def __init__(self) -> None:
        super().__init__("Send at least one field: title, description or status")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _now() -> str:
    """Current timestamp in ISO 8601 (UTC)."""
    return datetime.now(UTC).isoformat()


def _day_bounds(value: date) -> tuple[str, str]:
    """Half-open ISO bounds for a calendar day: ``[day 00:00, next day 00:00)``."""
    start = datetime(value.year, value.month, value.day, tzinfo=UTC)
    return start.isoformat(), (start + timedelta(days=1)).isoformat()


# --------------------------------------------------------------------------- #
# Repository
# --------------------------------------------------------------------------- #
class TodoRepository:
    """All persistence for the ``todos`` table. Returns dicts, raises nothing."""

    def __init__(
        self, connection_provider: ConnectionProvider = database.get_connection
    ):
        # A callable rather than a live connection: the shared connection can be
        # transparently reopened (tests swap ``TODOS_DB``), so we resolve it per
        # call, always under ``database.lock``.
        self._connection = connection_provider

    def list(
        self,
        status: str | None = None,
        date_field: str = "created",
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict]:
        """Return tasks, optionally filtered by status and an inclusive date range.

        ``date_field`` selects the timestamp the range applies to. ``limit`` /
        ``offset`` page the result (``limit=None`` returns everything). Date
        bounds are sargable (``col >= ? AND col < ?``) so the indexes are used.
        """
        column = DATE_COLUMNS.get(date_field, "created_at")
        clauses: list[str] = []
        params: list = []

        if status is not None:
            clauses.append("status = ?")
            params.append(status)
        if date_from is not None:
            clauses.append(f"{column} >= ?")
            params.append(_day_bounds(date_from)[0])
        if date_to is not None:
            clauses.append(f"{column} < ?")
            params.append(_day_bounds(date_to)[1])

        query = "SELECT * FROM todos"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY created_at DESC, id DESC"
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params += [limit, offset]

        with database.lock:
            rows = self._connection().execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def count_by_status(self) -> dict[str, int]:
        """Cheap aggregate for the dashboard summary (one indexed GROUP BY)."""
        with database.lock:
            rows = (
                self._connection()
                .execute("SELECT status, COUNT(*) AS n FROM todos GROUP BY status")
                .fetchall()
            )
        counts = {row["status"]: row["n"] for row in rows}
        pending, done = counts.get("pending", 0), counts.get("done", 0)
        return {"total": pending + done, "pending": pending, "done": done}

    def get(self, todo_id: int) -> dict | None:
        """Return a task by its id, or ``None`` if it does not exist."""
        with database.lock:
            row = (
                self._connection()
                .execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
                .fetchone()
            )
        return dict(row) if row is not None else None

    def add(
        self,
        title: str,
        description: str | None = None,
        created_at: str | None = None,
    ) -> dict:
        """Insert a new task (always ``pending``, never completed) and return it.

        ``created_at`` may be a ``YYYY-MM-DD`` string to backdate the task; it is
        stored as midnight UTC of that day. When omitted, the current instant is
        used.
        """
        timestamp = f"{created_at}T00:00:00+00:00" if created_at else _now()
        with database.lock, self._connection() as conn:
            row = conn.execute(
                "INSERT INTO todos "
                "(title, description, status, created_at, updated_at, completed_at) "
                "VALUES (?, ?, 'pending', ?, ?, NULL) RETURNING *",
                (title, description, timestamp, timestamp),
            ).fetchone()
        return dict(row)

    def update(self, todo_id: int, fields: dict) -> dict | None:
        """Update the given fields of a task; return it, or ``None`` if missing.

        ``fields`` may only contain ``title``, ``description`` and ``status``.
        ``completed_at`` is derived: stamped when a task first becomes ``done``
        and cleared when it goes back to ``pending``.
        """
        allowed = {"title", "description", "status"}
        updates = {k: v for k, v in fields.items() if k in allowed}

        with database.lock, self._connection() as conn:
            current = conn.execute(
                "SELECT status FROM todos WHERE id = ?", (todo_id,)
            ).fetchone()
            if current is None:
                return None
            if not updates:
                row = conn.execute(
                    "SELECT * FROM todos WHERE id = ?", (todo_id,)
                ).fetchone()
                return dict(row)

            if "status" in updates:
                if updates["status"] == "done" and current["status"] != "done":
                    updates["completed_at"] = _now()
                elif updates["status"] == "pending":
                    updates["completed_at"] = None

            updates["updated_at"] = _now()
            set_clause = ", ".join(f"{col} = ?" for col in updates)
            row = conn.execute(
                f"UPDATE todos SET {set_clause} WHERE id = ? RETURNING *",
                [*updates.values(), todo_id],
            ).fetchone()
        return dict(row)

    def delete(self, todo_id: int) -> bool:
        """Delete a task. Return ``True`` if a row was removed, ``False`` otherwise."""
        with database.lock, self._connection() as conn:
            deleted = conn.execute(
                "DELETE FROM todos WHERE id = ? RETURNING id", (todo_id,)
            ).fetchone()
        return deleted is not None


# --------------------------------------------------------------------------- #
# Service
# --------------------------------------------------------------------------- #
class TodoService:
    """Business rules over a :class:`TodoRepository`.

    The routes call these methods and never see ``None``: a missing task is a
    :class:`TodoNotFound`, an empty ``PATCH`` is an :class:`EmptyUpdate`.
    """

    def __init__(self, repository: TodoRepository | None = None) -> None:
        self.repo = repository or TodoRepository()

    def list_todos(
        self,
        status: str | None = None,
        date_field: str = "created",
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict]:
        # Enforce the page-size cap here too, not just at the route, so a direct
        # caller (tests, a future CLI) cannot ask for an unbounded result.
        capped = (
            DEFAULT_PAGE_SIZE if limit is None else max(1, min(limit, MAX_PAGE_SIZE))
        )
        return self.repo.list(
            status, date_field, date_from, date_to, capped, max(0, offset)
        )

    def stats(self) -> dict[str, int]:
        return self.repo.count_by_status()

    def get_todo(self, todo_id: int) -> dict:
        todo = self.repo.get(todo_id)
        if todo is None:
            raise TodoNotFound(todo_id)
        return todo

    def create_todo(
        self,
        title: str,
        description: str | None = None,
        created_at: str | None = None,
    ) -> dict:
        return self.repo.add(title, description, created_at)

    def update_todo(self, todo_id: int, fields: dict) -> dict:
        if not fields:
            raise EmptyUpdate()
        updated = self.repo.update(todo_id, fields)
        if updated is None:
            raise TodoNotFound(todo_id)
        return updated

    def delete_todo(self, todo_id: int) -> None:
        if not self.repo.delete(todo_id):
            raise TodoNotFound(todo_id)
