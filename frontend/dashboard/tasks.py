"""Pure transforms over lists of task dicts. No Streamlit, no I/O."""


def summarize(todos: list[dict]) -> tuple[int, int, int]:
    """Return ``(total, done, pending)`` counts."""
    total = len(todos)
    done = sum(1 for t in todos if t["status"] == "done")
    return total, done, total - done


def sort_pending_first(todos: list[dict]) -> list[dict]:
    """Pending tasks before done ones; order within each group is preserved."""
    return sorted(todos, key=lambda t: t["status"] == "done")
