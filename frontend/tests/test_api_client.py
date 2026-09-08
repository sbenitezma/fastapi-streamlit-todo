"""Unit tests for app.api_client. The HTTP layer is mocked; no server needed."""

from datetime import date
from unittest.mock import patch

import pytest
import requests

from dashboard import api_client
from dashboard.api_client import APIError


class FakeResponse:
    def __init__(self, status_code=200, json_body=None, text=""):
        self.status_code = status_code
        self._json = json_body
        self.text = text

    def json(self):
        if self._json is None:
            raise ValueError("no json")
        return self._json


def _patch_request(**kwargs):
    return patch.object(api_client._session, "request", **kwargs)


# --- fetch_todos ---------------------------------------------------------- #
def test_fetch_todos_drops_empty_params_and_returns_json():
    with _patch_request(return_value=FakeResponse(json_body=[{"id": 1}])) as m:
        result = api_client.fetch_todos(status="pending", date_from=None, date_to="")
    assert result == [{"id": 1}]
    method, url = m.call_args.args
    assert method == "GET" and url.endswith("/todos")
    assert m.call_args.kwargs["params"] == {"status": "pending"}


# --- fetch_stats ------------------------------------------------------- #
def test_fetch_stats():
    body = {"total": 3, "pending": 2, "done": 1}
    with _patch_request(return_value=FakeResponse(json_body=body)) as m:
        assert api_client.fetch_stats() == body
    method, url = m.call_args.args
    assert method == "GET" and url.endswith("/todos/stats")


# --- create_todo -------------------------------------------------------- #
def test_create_todo_strips_and_omits_blank_description():
    with _patch_request(
        return_value=FakeResponse(status_code=201, json_body={"id": 9})
    ) as m:
        api_client.create_todo("  Buy milk  ", "   ")
    assert m.call_args.kwargs["json"] == {"title": "Buy milk"}


def test_create_todo_includes_backdate():
    with _patch_request(
        return_value=FakeResponse(status_code=201, json_body={"id": 9})
    ) as m:
        api_client.create_todo("Old", "note", date(2024, 1, 15))
    assert m.call_args.kwargs["json"] == {
        "title": "Old",
        "description": "note",
        "created_at": "2024-01-15",
    }


# --- set_status / delete_todo ----------------------------------------- #
def test_set_status_patches_only_status():
    with _patch_request(return_value=FakeResponse(json_body={"id": 3})) as m:
        api_client.set_status(3, "done")
    method, url = m.call_args.args
    assert method == "PATCH" and url.endswith("/todos/3")
    assert m.call_args.kwargs["json"] == {"status": "done"}


def test_delete_todo_calls_delete():
    with _patch_request(return_value=FakeResponse(status_code=204)) as m:
        api_client.delete_todo(7)
    method, url = m.call_args.args
    assert method == "DELETE" and url.endswith("/todos/7")


# --- error handling --------------------------------------------------- #
def test_error_status_raises_apierror_with_detail():
    resp = FakeResponse(status_code=404, json_body={"detail": "No task with id 7"})
    with _patch_request(return_value=resp):
        with pytest.raises(APIError) as exc:
            api_client.fetch_todos()
    assert "404" in str(exc.value) and "No task with id 7" in str(exc.value)


def test_connection_error_is_wrapped():
    with _patch_request(side_effect=requests.exceptions.ConnectionError()):
        with pytest.raises(APIError) as exc:
            api_client.fetch_todos()
    assert "Cannot reach the API" in str(exc.value)
