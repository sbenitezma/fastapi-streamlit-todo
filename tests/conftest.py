"""Shared test configuration.

Every test runs against an empty, temporary SQLite database isolated from the
rest. This is achieved by pointing the ``TODOS_DB`` environment variable at a
file inside ``tmp_path`` before creating the ``TestClient``.
"""

import pytest
from fastapi.testclient import TestClient

from api import database
from api.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test_todos.db"
    monkeypatch.setenv("TODOS_DB", str(db_file))
    database.close_connection()  # drop any connection from a previous test
    database.init_db()
    with TestClient(app) as test_client:
        yield test_client
    database.close_connection()
