"""Unit tests for the persistence layer: TodoRepository + TodoService.

No HTTP and no TestClient -- these exercise the service directly against a
temporary SQLite database (the same isolation trick ``conftest`` uses for the
API tests).
"""

import pytest

from api import database
from api.todos_service import (
    EmptyUpdate,
    TodoNotFound,
    TodoRepository,
    TodoService,
)


@pytest.fixture()
def service(tmp_path, monkeypatch):
    monkeypatch.setenv("TODOS_DB", str(tmp_path / "service_todos.db"))
    database.close_connection()  # drop any connection from a previous test
    database.init_db()
    yield TodoService(TodoRepository())
    database.close_connection()


# --------------------------------------------------------------------------- #
# create
# --------------------------------------------------------------------------- #
def test_create_defaults_to_pending_and_uncompleted(service):
    todo = service.create_todo("Write tests")
    assert todo["id"] > 0
    assert todo["status"] == "pending"
    assert todo["completed_at"] is None
    assert todo["created_at"] == todo["updated_at"]


def test_create_backdated_stores_midnight_utc(service):
    todo = service.create_todo("Old task", created_at="2024-01-15")
    assert todo["created_at"] == "2024-01-15T00:00:00+00:00"
    assert todo["updated_at"] == "2024-01-15T00:00:00+00:00"


# --------------------------------------------------------------------------- #
# get
# --------------------------------------------------------------------------- #
def test_get_missing_raises_todo_not_found(service):
    with pytest.raises(TodoNotFound) as exc:
        service.get_todo(999)
    assert exc.value.todo_id == 999
    assert "999" in str(exc.value)


# --------------------------------------------------------------------------- #
# update
# --------------------------------------------------------------------------- #
def test_update_without_fields_raises_empty_update(service):
    todo = service.create_todo("Something")
    with pytest.raises(EmptyUpdate):
        service.update_todo(todo["id"], {})


def test_update_missing_raises_todo_not_found(service):
    with pytest.raises(TodoNotFound):
        service.update_todo(999, {"title": "x"})


def test_update_ignores_unknown_fields(service):
    todo = service.create_todo("Guard")
    updated = service.update_todo(todo["id"], {"title": "kept", "bogus": "dropped"})
    assert updated["title"] == "kept"
    assert "bogus" not in updated


def test_completed_at_is_stamped_and_cleared(service):
    todo = service.create_todo("Track me")

    done = service.update_todo(todo["id"], {"status": "done"})
    assert done["completed_at"] is not None
    assert done["completed_at"] >= done["created_at"]

    reopened = service.update_todo(todo["id"], {"status": "pending"})
    assert reopened["completed_at"] is None


def test_completed_at_not_restamped_when_already_done(service):
    todo = service.create_todo("Idempotent done")
    first = service.update_todo(todo["id"], {"status": "done"})
    again = service.update_todo(todo["id"], {"status": "done"})
    assert again["completed_at"] == first["completed_at"]


# --------------------------------------------------------------------------- #
# delete
# --------------------------------------------------------------------------- #
def test_delete_removes_and_second_delete_raises(service):
    todo = service.create_todo("Ephemeral")
    service.delete_todo(todo["id"])
    with pytest.raises(TodoNotFound):
        service.delete_todo(todo["id"])


# --------------------------------------------------------------------------- #
# stats
# --------------------------------------------------------------------------- #
def test_stats_counts_by_status(service):
    first = service.create_todo("a")
    service.create_todo("b")
    service.create_todo("c")
    service.update_todo(first["id"], {"status": "done"})
    assert service.stats() == {"total": 3, "pending": 2, "done": 1}


def test_stats_empty(service):
    assert service.stats() == {"total": 0, "pending": 0, "done": 0}


# --------------------------------------------------------------------------- #
# repository-level filtering / ordering / paging
# --------------------------------------------------------------------------- #
def test_repository_status_filter_and_default_ordering(service):
    repo = service.repo
    older = service.create_todo("first")
    newer = service.create_todo("second")
    service.update_todo(older["id"], {"status": "done"})

    assert [t["id"] for t in repo.list(status="pending")] == [newer["id"]]
    # created_at DESC, id DESC -> newest first
    assert [t["id"] for t in repo.list()] == [newer["id"], older["id"]]


def test_repository_pagination(service):
    ids = [service.create_todo(f"t{i}")["id"] for i in range(5)]
    newest_first = list(reversed(ids))
    assert [t["id"] for t in service.repo.list(limit=2)] == newest_first[:2]
    assert [t["id"] for t in service.repo.list(limit=2, offset=2)] == newest_first[2:4]
