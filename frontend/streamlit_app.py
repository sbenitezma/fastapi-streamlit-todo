"""Task Manager dashboard -- Streamlit entry point.

A thin client over the REST API; it never touches the database. Run with:

    streamlit run frontend/streamlit_app.py

Structure:

    components/   reusable, accessible render functions (badge, chip, card,
                  meter, pager, confirm_button, empty_state, load, ...)
    config        constants and option maps
    api_client    the only outward boundary (HTTP, keep-alive session)
    data          st.cache_data layer -- reruns that don't change data cost 0 calls
    formatting /  pure helpers                          (unit tested)
    tasks / filtering
    filters       the inline filter bar + chips
    styles        design tokens + component CSS
    theme         Light / Dark / System switch
    views/        sidebar, summary and task-list composition
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from app.api_client import APIError
from app.components import empty_state, load, pager
from app.data import load_stats, load_todos
from app.filters import render_active_filters, render_filter_bar
from app.styles import inject_styles
from app.theme import render_theme_control, seed_theme_state
from app.views.sidebar import render_create_form
from app.views.summary import render_summary
from app.views.task_list import render_task_list

PAGE_SIZE = 50

st.set_page_config(
    page_title="Task Manager",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="expanded",
)

seed_theme_state()
inject_styles()
st.session_state.setdefault("page", 0)


def _go_to_page(page: int) -> None:
    st.session_state["page"] = max(0, page)


def _clear_all_filters() -> None:
    st.session_state["f_status"] = "All"
    st.session_state["f_field"] = "Created"
    st.session_state["f_from"] = st.session_state["f_to"] = None
    st.session_state["page"] = 0


with st.sidebar:
    render_theme_control()
    st.divider()
    render_create_form()

st.title("✅ Task Manager")

stats = load(
    load_stats, key="stats", spinner="Loading summary…", error_types=(APIError,)
)
render_summary(stats)

st.header("Tasks")
filters = render_filter_bar()
render_active_filters(filters)

# Reset to page 1 whenever the filter selection changes.
signature = tuple(sorted(filters.to_query().items()))
if st.session_state.get("_filter_sig") != signature:
    st.session_state["_filter_sig"] = signature
    st.session_state["page"] = 0
page = st.session_state["page"]

query = dict(signature, limit=str(PAGE_SIZE), offset=str(page * PAGE_SIZE))
shown = load(
    lambda: load_todos(tuple(sorted(query.items()))),
    key="todos",
    spinner="Loading tasks…",
    error_types=(APIError,),
)

if not shown:
    if stats["total"] == 0:
        empty_state(
            "No tasks yet",
            body="Add your first one from the sidebar.",
            icon="✅",
            key="empty-none",
        )
    else:
        empty_state(
            "Nothing matches this view",
            body="Try a different filter or go back a page.",
            icon="🔍",
            action_label="Clear all filters" if filters.active else None,
            on_action=_clear_all_filters if filters.active else None,
            key="empty-filtered",
        )
else:
    start = page * PAGE_SIZE
    st.caption(
        f"Showing {start + 1}–{start + len(shown)}"
        + (" · filtered" if filters.active else "")
    )
    render_task_list(shown, grouped=not filters.status)
    pager(
        key="pager",
        page=page,
        has_next=len(shown) == PAGE_SIZE,
        on_change=_go_to_page,
    )
