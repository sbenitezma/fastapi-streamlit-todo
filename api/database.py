"""SQLite engine layer: connection, schema and pragmas (no ORM).

A :class:`Database` owns one SQLite connection for its lifetime. It knows nothing
about tasks -- every query for the ``todos`` table lives in the Repository in
:mod:`api.todos_service`, which borrows the connection under :attr:`Database.lock`.

The app builds one ``Database`` in its lifespan and stores it on ``app.state``;
tests build their own against a temp file. There is no module-level connection.

Performance notes:
* One WAL-mode connection per ``Database`` (not one per call). Access is
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


def default_db_path() -> str:
    """Path of the SQLite file: the ``TODOS_DB`` env var, else ``todos.db``."""
    return os.environ.get("TODOS_DB", DEFAULT_DB_PATH)


class Database:
    """A single SQLite connection plus the lock that serializes access to it."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.lock = threading.RLock()
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        """Return the connection, opening it (with pragmas) on first use."""
        with self.lock:
            if self._conn is None:
                conn = sqlite3.connect(self.path, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA busy_timeout=5000")
                conn.execute("PRAGMA foreign_keys=ON")
                self._conn = conn
            return self._conn

    def close(self) -> None:
        with self.lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None

    def init_schema(self) -> None:
        """Create the table and indexes if needed; apply small forward migrations."""
        with self.lock:
            conn = self.connect()
            conn.executescript(_SCHEMA)
            columns = {row["name"] for row in conn.execute("PRAGMA table_info(todos)")}
            if "completed_at" not in columns:
                conn.execute("ALTER TABLE todos ADD COLUMN completed_at TEXT")
            conn.commit()
