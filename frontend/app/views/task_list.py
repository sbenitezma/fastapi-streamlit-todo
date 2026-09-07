"""Task list: one card per task (built from the component library) with inline actions."""

from collections.abc import Callable
from html import escape

import streamlit as st

from app.api_client import APIError, delete_todo, set_status
from app.components import badge_html, card, confirm_button, truncate
from app.data import invalidate
from app.formatting import task_timeline
from app.tasks import sort_pending_first


def render_task_list(todos: list[dict], *, grouped: bool) -> None:
    """Render every task, pending first. ``grouped`` inserts a 'Completed' divider."""
    divider_done = False
    for todo in sort_pending_first(todos):
        if grouped and todo["status"] == "done" and not divider_done:
            st.caption("Completed")
            divider_done = True
        _render_row(todo)


def _render_row(todo: dict) -> None:
    is_pending = todo["status"] == "pending"
    box = card(
        accent="warning" if is_pending else "success",
        muted=not is_pending,
        key=str(todo["id"]),
    )
    with box:
        main, side = st.columns([5, 2], gap="small", vertical_alignment="center")
        with main:
            _render_details(todo, is_pending)
        with side:
            _render_actions(todo, is_pending)


def _render_details(todo: dict, is_pending: bool) -> None:
    tone, badge_label = ("warning", "◷ Pending") if is_pending else ("success", "✓ Done")
    title_class = "tm-title" if is_pending else "tm-title tm-title--done"
    title, _ = truncate(todo["title"], 160)

    html = [
        f'<div class="{title_class}" title="{escape(todo["title"])}">'
        f'{escape(title)}{badge_html(badge_label, tone=tone)}</div>'
    ]
    if todo["description"]:
        html.append(f'<div class="tm-desc">{escape(todo["description"])}</div>')
    html.append(f'<div class="tm-dates">{escape(task_timeline(todo))}</div>')
    st.markdown("".join(html), unsafe_allow_html=True)


def _render_actions(todo: dict, is_pending: bool) -> None:
    if is_pending:
        if st.button(
            "Complete", key=f"done-{todo['id']}", type="primary", width="stretch",
            help=f'Mark "{todo["title"]}" as done',
        ):
            _run(lambda: set_status(todo["id"], "done"), "Task completed", "✅")
    elif st.button(
        "Reopen", key=f"reopen-{todo['id']}", width="stretch",
        help=f'Move "{todo["title"]}" back to pending',
    ):
        _run(lambda: set_status(todo["id"], "pending"), "Task reopened", None)

    if confirm_button(
        "Delete", key=f"del-{todo['id']}", title=todo["title"],
        confirm_label="Yes, delete", help=f'Delete "{todo["title"]}"',
    ):
        _run(lambda: delete_todo(todo["id"]), "Task deleted", "🗑️")


def _run(action: Callable[[], object], toast: str, icon: str | None) -> None:
    try:
        action()
        invalidate()  # the cached task list / stats are now stale
        st.toast(toast, icon=icon) if icon else st.toast(toast)
        st.rerun()
    except APIError as exc:
        st.error(str(exc))
