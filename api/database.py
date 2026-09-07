"""Data access with the standard library ``sqlite3`` module (no ORM).

All persistence logic lives here. API routes never write SQL directly: they call
the helpers in this module, which return plain dictionaries and always use
parameterized queries.
"""

import os
import sqlite3
from datetime import datetime, timezone

DEFAULT_DB_PATH = "todos.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS todos (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT NOT NULL,
    description  TEXT,
    status       TEXT NOT NULL DEFAULT 'pending'
                 CHECK (status IN ('pending', 'done')),
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL,
    completed_at TEXT
);
"""

# Date columns that ``list_todos`` is allowed to filter on. The mapping doubles
# as a whitelist: only these values can ever reach an SQL string.
DATE_COLUMNS = {
    "created": "created_at",
    "updated": "updated_at",
    "completed": "completed_at",
}


def get_db_path() -> str:
    """Path of the SQLite file.

    Read on every call (never cached) so tests can point to a throwaway database
    through the ``TODOS_DB`` environment variable.
    """
    return os.environ.get("TODOS_DB", DEFAULT_DB_PATH)


def _now() -> str:
    """Current timestamp in ISO 8601 (UTC)."""
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    """Open a fresh connection with ``row_factory`` so rows behave like dicts."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the table if needed and apply small forward migrations."""
    with get_connection() as conn:
        conn.executescript(_SCHEMA)
        # Databases created before ``completed_at`` existed get the column added.
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(todos)")}
        if "completed_at" not in columns:
            conn.execute("ALTER TABLE todos ADD COLUMN completed_at TEXT")


def _row_to_dict(row: sqlite3.Row | None) -> dict | None:
    return dict(row) if row is not None else None


def list_todos(
    status: str | None = None,
    date_field: str = "created",
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[dict]:
    """Return tasks, optionally filtered by status and by a date range.

    ``date_field`` picks which timestamp the range applies to (``created``,
    ``updated`` or ``completed``). ``date_from`` / ``date_to`` are inclusive
    ``YYYY-MM-DD`` strings; they are compared against the first 10 characters of
    the stored ISO timestamp.
    """
    column = DATE_COLUMNS.get(date_field, "created_at")
    clauses: list[str] = []
    params: list = []

    if status is not None:
        clauses.append("status = ?")
        params.append(status)
    if date_from is not None:
        clauses.append(f"substr({column}, 1, 10) >= ?")
        params.append(date_from)
    if date_to is not None:
        clauses.append(f"substr({column}, 1, 10) <= ?")
        params.append(date_to)

    query = "SELECT * FROM todos"
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY created_at DESC, id DESC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def get_todo(todo_id: int) -> dict | None:
    """Return a task by its id, or ``None`` if it does not exist."""
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    return _row_to_dict(row)


def create_todo(
    title: str,
    description: str | None = None,
    created_at: str | None = None,
) -> dict:
    """Insert a new task (always ``pending``, never completed) and return it.

    ``created_at`` may be a ``YYYY-MM-DD`` string to backdate the task; it is
    stored as midnight UTC of that day. When omitted, the current instant is used.
    """
    timestamp = f"{created_at}T00:00:00+00:00" if created_at else _now()
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO todos "
            "(title, description, status, created_at, updated_at, completed_at) "
            "VALUES (?, ?, 'pending', ?, ?, NULL)",
            (title, description, timestamp, timestamp),
        )
        new_id = cursor.lastrowid
    return get_todo(new_id)


def update_todo(todo_id: int, fields: dict) -> dict | None:
    """Update the given fields of a task.

    ``fields`` must only contain keys among ``title``, ``description`` and
    ``status``. Returns ``None`` if the task does not exist.

    ``completed_at`` is derived, not client-controlled: it is stamped when a task
    first becomes ``done`` and cleared when it goes back to ``pending``.
    """
    allowed = {"title", "description", "status"}
    updates = {k: v for k, v in fields.items() if k in allowed}

    current = get_todo(todo_id)
    if current is None:
        return None
    if not updates:
        return current

    if "status" in updates:
        if updates["status"] == "done" and current["status"] != "done":
            updates["completed_at"] = _now()
        elif updates["status"] == "pending":
            updates["completed_at"] = None

    updates["updated_at"] = _now()
    set_clause = ", ".join(f"{col} = ?" for col in updates)
    params = list(updates.values()) + [todo_id]
    with get_connection() as conn:
        conn.execute(f"UPDATE todos SET {set_clause} WHERE id = ?", params)
    return get_todo(todo_id)


def delete_todo(todo_id: int) -> bool:
    """Delete a task. Return ``True`` if a row was removed, ``False`` otherwise."""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        return cursor.rowcount > 0
