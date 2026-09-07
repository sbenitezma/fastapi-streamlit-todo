"""Task list: one bordered card per task with inline actions."""

from collections.abc import Callable
from html import escape

import streamlit as st

from app.api_client import APIError, delete_todo, set_status
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
    with st.container(border=True):
        main, side = st.columns([5, 2], gap="small", vertical_alignment="center")
        with main:
            _render_details(todo, is_pending)
        with side:
            _render_actions(todo, is_pending)


def _render_details(todo: dict, is_pending: bool) -> None:
    flag = "pending" if is_pending else "done"
    badge = "◷ Pending" if is_pending else "✓ Done"
    title_class = "tm-title" if is_pending else "tm-title done"

    html = [
        f'<span class="tm-flag {flag}" hidden></span>',
        f'<div class="{title_class}">{escape(todo["title"])}'
        f'<span class="tm-badge {flag}">{badge}</span></div>',
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
    else:
        if st.button(
            "Reopen", key=f"reopen-{todo['id']}", width="stretch",
            help=f'Move "{todo["title"]}" back to pending',
        ):
            _run(lambda: set_status(todo["id"], "pending"), "Task reopened", None)

    with st.popover("Delete", width="stretch"):
        st.markdown(f'Delete **{escape(todo["title"])}**? This cannot be undone.')
        if st.button(
            "Yes, delete", key=f"del-{todo['id']}", type="primary", width="stretch",
        ):
            _run(lambda: delete_todo(todo["id"]), "Task deleted", "🗑️")


def _run(action: Callable[[], object], toast: str, icon: str | None) -> None:
    try:
        action()
        st.toast(toast, icon=icon) if icon else st.toast(toast)
        st.rerun()
    except APIError as exc:
        st.error(str(exc))
