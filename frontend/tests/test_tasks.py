"""Unit tests for app.tasks (pure, no Streamlit)."""

from dashboard.tasks import sort_pending_first, summarize


def _todo(id_, status):
    return {"id": id_, "status": status}


def test_summarize_empty():
    assert summarize([]) == (0, 0, 0)


def test_summarize_counts():
    todos = [_todo(1, "pending"), _todo(2, "done"), _todo(3, "done")]
    assert summarize(todos) == (3, 2, 1)


def test_sort_pending_first_is_stable():
    todos = [
        _todo(1, "done"),
        _todo(2, "pending"),
        _todo(3, "done"),
        _todo(4, "pending"),
    ]
    ordered = [t["id"] for t in sort_pending_first(todos)]
    assert ordered == [2, 4, 1, 3]


def test_sort_pending_first_does_not_mutate_input():
    todos = [_todo(1, "done"), _todo(2, "pending")]
    sort_pending_first(todos)
    assert [t["id"] for t in todos] == [1, 2]
