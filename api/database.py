"""Data access with the standard library ``sqlite3`` module (no ORM).

All persistence logic lives here. API routes never write SQL directly: they call
the helpers in this module, which return plain dictionaries and always use
parameterized queries.

Performance notes:
* One WAL-mode connection is kept open per process (not one per call). Access is
  serialized with a re-entrant lock -- SQLite is fast enough that the lock is
  never the bottleneck for this workload, and it removes a class of threading /
  ``SQLITE_BUSY`` bugs. For heavier concurrency, switch to a reader pool.
* Indexes back the list query's ``WHERE`` and ``ORDER BY`` so it never scans or
  builds a temp b-tree.
* Date ranges use sargable ``col >= ? AND col < ?`` bounds (index-friendly)
  instead of ``substr(col, 1, 10)`` (which forces a scan).
* ``INSERT``/``UPDATE``/``DELETE`` use ``RETURNING`` so the row is returned in a
  single round trip instead of a follow-up ``SELECT``.
"""

import os
import sqlite3
import threading
from datetime import date, datetime, timedelta, timezone

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
CREATE INDEX IF NOT EXISTS idx_todos_created
    ON todos (created_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_todos_status_created
    ON todos (status, created_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_todos_updated   ON todos (updated_at);
CREATE INDEX IF NOT EXISTS idx_todos_completed ON todos (completed_at);
"""

# Date columns that ``list_todos`` is allowed to filter on. The mapping doubles
# as a whitelist: only these values can ever reach an SQL string.
DATE_COLUMNS = {
    "created": "created_at",
    "updated": "updated_at",
    "completed": "completed_at",
}

_lock = threading.RLock()
_conn: sqlite3.Connection | None = None
_conn_path: str | None = None


def get_db_path() -> str:
    """Path of the SQLite file (from ``TODOS_DB``; tests point it at a temp file)."""
    return os.environ.get("TODOS_DB", DEFAULT_DB_PATH)


def _now() -> str:
    """Current timestamp in ISO 8601 (UTC)."""
    return datetime.now(timezone.utc).isoformat()


def get_connection() -> sqlite3.Connection:
    """Return the shared connection, (re)opening it if the target path changed."""
    global _conn, _conn_path
    path = get_db_path()
    with _lock:
        if _conn is not None and _conn_path == path:
            return _conn
        if _conn is not None:
            _conn.close()
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA foreign_keys=ON")
        _conn, _conn_path = conn, path
        return conn


def close_connection() -> None:
    """Close the shared connection (used by tests between temp databases)."""
    global _conn, _conn_path
    with _lock:
        if _conn is not None:
            _conn.close()
        _conn = _conn_path = None


def init_db() -> None:
    """Create the table and indexes if needed and apply small forward migrations."""
    with _lock:
        conn = get_connection()
        conn.executescript(_SCHEMA)
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(todos)")}
        if "completed_at" not in columns:
            conn.execute("ALTER TABLE todos ADD COLUMN completed_at TEXT")
        conn.commit()


def _day_bounds(value: date) -> tuple[str, str]:
    """Half-open ISO bounds for a calendar day: ``[day 00:00, next day 00:00)``."""
    start = datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    return start.isoformat(), (start + timedelta(days=1)).isoformat()


def list_todos(
    status: str | None = None,
    date_field: str = "created",
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int | None = None,
    offset: int = 0,
) -> list[dict]:
    """Return tasks, optionally filtered by status and an inclusive date range.

    ``date_field`` selects the timestamp the range applies to. ``limit`` /
    ``offset`` page the result (``limit=None`` returns everything).
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

    with _lock:
        rows = get_connection().execute(query, params).fetchall()
    return [dict(row) for row in rows]


def count_by_status() -> dict[str, int]:
    """Cheap aggregate for the dashboard summary (one indexed GROUP BY)."""
    with _lock:
        rows = get_connection().execute(
            "SELECT status, COUNT(*) AS n FROM todos GROUP BY status"
        ).fetchall()
    counts = {row["status"]: row["n"] for row in rows}
    pending, done = counts.get("pending", 0), counts.get("done", 0)
    return {"total": pending + done, "pending": pending, "done": done}


def get_todo(todo_id: int) -> dict | None:
    """Return a task by its id, or ``None`` if it does not exist."""
    with _lock:
        row = get_connection().execute(
            "SELECT * FROM todos WHERE id = ?", (todo_id,)
        ).fetchone()
    return dict(row) if row is not None else None


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
    with _lock, get_connection() as conn:
        row = conn.execute(
            "INSERT INTO todos "
            "(title, description, status, created_at, updated_at, completed_at) "
            "VALUES (?, ?, 'pending', ?, ?, NULL) RETURNING *",
            (title, description, timestamp, timestamp),
        ).fetchone()
    return dict(row)


def update_todo(todo_id: int, fields: dict) -> dict | None:
    """Update the given fields of a task; return it, or ``None`` if it is missing.

    ``fields`` may only contain ``title``, ``description`` and ``status``.
    ``completed_at`` is derived: stamped when a task first becomes ``done`` and
    cleared when it goes back to ``pending``.
    """
    allowed = {"title", "description", "status"}
    updates = {k: v for k, v in fields.items() if k in allowed}

    with _lock, get_connection() as conn:
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


def delete_todo(todo_id: int) -> bool:
    """Delete a task. Return ``True`` if a row was removed, ``False`` otherwise."""
    with _lock, get_connection() as conn:
        deleted = conn.execute(
            "DELETE FROM todos WHERE id = ? RETURNING id", (todo_id,)
        ).fetchone()
    return deleted is not None
