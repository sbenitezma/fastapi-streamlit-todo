"""Pure string formatting for task data. No Streamlit, no I/O."""

from datetime import datetime


def human_date(iso: str | None) -> str:
    """Render an ISO timestamp as e.g. ``7 Sep 2026, 10:15``.

    The time is dropped when it is exactly midnight (backdated tasks).
    """
    if not iso:
        return "—"
    dt = datetime.fromisoformat(iso)
    if (dt.hour, dt.minute) == (0, 0):
        return f"{dt.day} {dt:%b %Y}"
    return f"{dt.day} {dt:%b %Y}, {dt:%H:%M}"


def task_timeline(todo: dict) -> str:
    """One-line ``Created … · Updated … · Done …`` summary for a task."""
    parts = [f"Created {human_date(todo['created_at'])}"]
    if todo.get("updated_at") and todo["updated_at"] != todo["created_at"]:
        parts.append(f"Updated {human_date(todo['updated_at'])}")
    if todo.get("completed_at"):
        parts.append(f"Done {human_date(todo['completed_at'])}")
    return " · ".join(parts)
