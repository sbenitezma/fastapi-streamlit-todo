"""The dashboard's only boundary with the outside world.

Every call to the REST API goes through here. Functions return plain data
(``dict`` / ``list``) or raise :class:`APIError`; they never import Streamlit, so
they can be unit tested without a running app.
"""

from datetime import date

import requests

from app.config import API_TIMEOUT, API_URL


class APIError(Exception):
    """Raised when the API is unreachable or replies with an error status."""


def _request(method: str, path: str, **kwargs) -> requests.Response:
    try:
        resp = requests.request(
            method, f"{API_URL}{path}", timeout=API_TIMEOUT, **kwargs
        )
    except requests.exceptions.ConnectionError as exc:
        raise APIError(
            f"Cannot reach the API at {API_URL}. Is it running? (`python -m api.main`)"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise APIError(f"Network error while calling the API: {exc}") from exc

    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        raise APIError(f"The API responded {resp.status_code}: {detail}")
    return resp


def fetch_todos(**params) -> list[dict]:
    """GET /todos, dropping empty query parameters."""
    query = {k: v for k, v in params.items() if v not in (None, "")}
    return _request("GET", "/todos", params=query).json()


def create_todo(title: str, description: str, created_on: date | None = None) -> dict:
    """POST /todos. ``created_on`` backdates the task when given."""
    payload: dict[str, str] = {"title": title.strip()}
    if description.strip():
        payload["description"] = description.strip()
    if created_on is not None:
        payload["created_at"] = created_on.isoformat()
    return _request("POST", "/todos", json=payload).json()


def set_status(todo_id: int, new_status: str) -> dict:
    """PATCH /todos/{id} to change only the status."""
    return _request("PATCH", f"/todos/{todo_id}", json={"status": new_status}).json()


def delete_todo(todo_id: int) -> None:
    """DELETE /todos/{id}."""
    _request("DELETE", f"/todos/{todo_id}")
