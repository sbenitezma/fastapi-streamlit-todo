"""Shared test configuration.

Every test runs against an empty, temporary SQLite database isolated from the
rest: ``TODOS_DB`` is pointed at a file inside ``tmp_path`` before the
``TestClient`` enters, so the app's lifespan builds its ``Database`` there,
creates the schema, and closes it on exit.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("TODOS_DB", str(tmp_path / "test_todos.db"))
    with TestClient(app) as test_client:
        yield test_client
