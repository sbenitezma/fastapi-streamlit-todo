"""Automated API tests. At least one per endpoint.

Uses FastAPI's ``TestClient`` (built on top of httpx).
"""

from datetime import date, timedelta


def _create(client, title="Test task", description=None):
    payload = {"title": title}
    if description is not None:
        payload["description"] = description
    return client.post("/api/todos", json=payload)


# --------------------------------------------------------------------------- #
# POST /api/todos
# --------------------------------------------------------------------------- #
def test_create_task(client):
    resp = _create(client, "Buy bread", "From the corner bakery")
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] > 0
    assert body["title"] == "Buy bread"
    assert body["description"] == "From the corner bakery"
    assert body["status"] == "pending"
    assert body["created_at"] and body["updated_at"]
    assert body["completed_at"] is None


def test_create_task_without_description(client):
    body = _create(client, "No description").json()
    assert body["description"] is None


def test_create_task_blank_title_is_422(client):
    resp = client.post("/api/todos", json={"title": "   "})
    assert resp.status_code == 422


def test_create_task_missing_title_is_422(client):
    resp = client.post("/api/todos", json={"description": "description only"})
    assert resp.status_code == 422


def test_create_task_backdated(client):
    past = "2024-01-15"
    body = client.post(
        "/api/todos", json={"title": "Old task", "created_at": past}
    ).json()
    assert body["created_at"].startswith(past)
    assert body["updated_at"].startswith(past)
    assert body["status"] == "pending"


def test_create_task_future_date_is_422(client):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    resp = client.post(
        "/api/todos", json={"title": "From the future", "created_at": tomorrow}
    )
    assert resp.status_code == 422


# --------------------------------------------------------------------------- #
# GET /api/todos  (+ status filter)
# --------------------------------------------------------------------------- #
def test_list_tasks_and_status_filter(client):
    id_a = _create(client, "Pending A").json()["id"]
    id_b = _create(client, "Will be completed B").json()["id"]
    client.patch(f"/api/todos/{id_b}", json={"status": "done"})

    all_tasks = client.get("/api/todos")
    assert all_tasks.status_code == 200
    assert {t["id"] for t in all_tasks.json()} == {id_a, id_b}

    pending = client.get("/api/todos", params={"status": "pending"}).json()
    assert [t["id"] for t in pending] == [id_a]

    done = client.get("/api/todos", params={"status": "done"}).json()
    assert [t["id"] for t in done] == [id_b]


def test_list_tasks_invalid_status_is_422(client):
    resp = client.get("/api/todos", params={"status": "garbage"})
    assert resp.status_code == 422


# --------------------------------------------------------------------------- #
# GET /api/todos  (+ date filter)
# --------------------------------------------------------------------------- #
def test_date_filter_on_created(client):
    _create(client, "Task A")
    _create(client, "Task B")
    today = date.today().isoformat()

    assert len(client.get("/api/todos", params={"date_from": today}).json()) == 2
    assert client.get("/api/todos", params={"date_to": "2000-01-01"}).json() == []


def test_date_filter_on_completed_field(client):
    id_done = _create(client, "Gets completed").json()["id"]
    _create(client, "Stays pending")
    client.patch(f"/api/todos/{id_done}", json={"status": "done"})
    today = date.today().isoformat()

    result = client.get(
        "/api/todos", params={"date_field": "completed", "date_from": today}
    ).json()
    assert [t["id"] for t in result] == [id_done]


def test_date_filter_invalid_date_is_422(client):
    resp = client.get("/api/todos", params={"date_from": "not-a-date"})
    assert resp.status_code == 422


def test_pagination_with_limit_and_offset(client):
    ids = [_create(client, f"Task {i}").json()["id"] for i in range(5)]
    newest_first = list(reversed(ids))

    page1 = client.get("/api/todos", params={"limit": 2}).json()
    assert [t["id"] for t in page1] == newest_first[:2]

    page2 = client.get("/api/todos", params={"limit": 2, "offset": 2}).json()
    assert [t["id"] for t in page2] == newest_first[2:4]

    assert client.get("/api/todos", params={"limit": 0}).status_code == 422
    assert client.get("/api/todos", params={"limit": 1001}).status_code == 422


def test_list_without_limit_still_returns_matches(client):
    ids = {_create(client, f"Task {i}").json()["id"] for i in range(3)}
    assert {t["id"] for t in client.get("/api/todos").json()} == ids


def test_stats_endpoint(client):
    done_id = _create(client, "Finish").json()["id"]
    _create(client, "Pending 1")
    _create(client, "Pending 2")
    client.patch(f"/api/todos/{done_id}", json={"status": "done"})

    resp = client.get("/api/todos/stats")
    assert resp.status_code == 200
    assert resp.json() == {"total": 3, "pending": 2, "done": 1}


def test_stats_endpoint_empty(client):
    assert client.get("/api/todos/stats").json() == {
        "total": 0,
        "pending": 0,
        "done": 0,
    }


# --------------------------------------------------------------------------- #
# GET /api/todos/{id}
# --------------------------------------------------------------------------- #
def test_get_existing_task(client):
    created = _create(client, "Details").json()
    resp = client.get(f"/api/todos/{created['id']}")
    assert resp.status_code == 200
    assert resp.json() == created


def test_get_missing_task_is_404(client):
    resp = client.get("/api/todos/9999")
    assert resp.status_code == 404
    assert "9999" in resp.json()["detail"]


# --------------------------------------------------------------------------- #
# PATCH /api/todos/{id}
# --------------------------------------------------------------------------- #
def test_update_task(client):
    id_ = _create(client, "Old title").json()["id"]
    resp = client.patch(
        f"/api/todos/{id_}",
        json={"title": "New title", "status": "done"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "New title"
    assert body["status"] == "done"
    assert body["updated_at"] >= body["created_at"]


def test_completed_at_lifecycle(client):
    id_ = _create(client, "Track completion").json()["id"]

    done = client.patch(f"/api/todos/{id_}", json={"status": "done"}).json()
    assert done["completed_at"] is not None
    assert done["completed_at"] >= done["created_at"]

    reopened = client.patch(f"/api/todos/{id_}", json={"status": "pending"}).json()
    assert reopened["completed_at"] is None


def test_update_task_without_fields_is_400(client):
    id_ = _create(client, "Something").json()["id"]
    resp = client.patch(f"/api/todos/{id_}", json={})
    assert resp.status_code == 400


def test_update_missing_task_is_404(client):
    resp = client.patch("/api/todos/9999", json={"title": "Nothing"})
    assert resp.status_code == 404


def test_update_task_invalid_status_is_422(client):
    id_ = _create(client, "Something").json()["id"]
    resp = client.patch(f"/api/todos/{id_}", json={"status": "archived"})
    assert resp.status_code == 422


# --------------------------------------------------------------------------- #
# DELETE /api/todos/{id}
# --------------------------------------------------------------------------- #
def test_delete_task(client):
    id_ = _create(client, "To be deleted").json()["id"]
    resp = client.delete(f"/api/todos/{id_}")
    assert resp.status_code == 204
    assert client.get(f"/api/todos/{id_}").status_code == 404


def test_delete_missing_task_is_404(client):
    resp = client.delete("/api/todos/9999")
    assert resp.status_code == 404
