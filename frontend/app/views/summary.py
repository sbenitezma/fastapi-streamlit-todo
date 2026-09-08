"""Summary: a single compact progress line above the task list."""

from app.components import meter


def render_summary(stats: dict) -> None:
    """``stats`` is ``{total, pending, done}`` from ``GET /api/todos/stats``."""
    meter(
        stats["done"],
        stats["total"],
        label="done",
        note=f"{stats['pending']} pending" if stats["pending"] else None,
    )
