"""Unit tests for app.formatting (pure, no Streamlit)."""

from app.formatting import human_date, task_timeline


def test_human_date_none():
    assert human_date(None) == "—"
    assert human_date("") == "—"


def test_human_date_drops_midnight_time():
    assert human_date("2026-08-20T00:00:00+00:00") == "20 Aug 2026"


def test_human_date_keeps_real_time():
    assert human_date("2026-09-07T10:15:30+00:00") == "7 Sep 2026, 10:15"


def test_task_timeline_created_only():
    todo = {"created_at": "2026-09-07T10:00:00+00:00",
            "updated_at": "2026-09-07T10:00:00+00:00", "completed_at": None}
    assert task_timeline(todo) == "Created 7 Sep 2026, 10:00"


def test_task_timeline_with_update_and_completion():
    todo = {
        "created_at": "2026-09-01T09:00:00+00:00",
        "updated_at": "2026-09-05T12:30:00+00:00",
        "completed_at": "2026-09-05T12:30:00+00:00",
    }
    line = task_timeline(todo)
    assert line == (
        "Created 1 Sep 2026, 09:00 · Updated 5 Sep 2026, 12:30 · Done 5 Sep 2026, 12:30"
    )
