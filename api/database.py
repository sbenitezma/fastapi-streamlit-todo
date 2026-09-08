"""SQLite engine layer: connection, schema and pragmas (no ORM).

This module owns the *infrastructure* only -- opening the database, applying the
pragmas, creating the table and its indexes. It does **not** know anything about
tasks: every query for the ``todos`` table lives in the Repository in
:mod:`api.todos_service`, which borrows the connection guarded by :data:`lock`.

Performance notes:
* One WAL-mode connection is kept open per process (not one per call). Access is
  serialized with a re-entrant lock -- SQLite is fast enough that the lock is
  never the bottleneck for this workload, and it removes a class of threading /
  ``SQLITE_BUSY`` bugs. For heavier concurrency, switch to a reader pool.
* Indexes back the list query's ``WHERE`` and ``ORDER BY`` so it never scans or
  builds a temp b-tree.
"""

import os
import sqlite3
import threading

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

# Re-entrant lock that serializes every access to the shared connection. The
# Repository acquires it around each statement (``with database.lock: ...``).
lock = threading.RLock()

_conn: sqlite3.Connection | None = None
_conn_path: str | None = None


def get_db_path() -> str:
    """Path of the SQLite file (from ``TODOS_DB``; tests point it at a temp file)."""
    return os.environ.get("TODOS_DB", DEFAULT_DB_PATH)


def get_connection() -> sqlite3.Connection:
    """Return the shared connection, (re)opening it if the target path changed."""
    global _conn, _conn_path
    path = get_db_path()
    with lock:
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
    with lock:
        if _conn is not None:
            _conn.close()
        _conn = _conn_path = None


def init_db() -> None:
    """Create the table and indexes if needed and apply small forward migrations."""
    with lock:
        conn = get_connection()
        conn.executescript(_SCHEMA)
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(todos)")}
        if "completed_at" not in columns:
            conn.execute("ALTER TABLE todos ADD COLUMN completed_at TEXT")
        conn.commit()
