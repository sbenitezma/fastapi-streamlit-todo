"""Task Manager dashboard -- Streamlit entry point.

A thin client over the REST API; it never touches the database. Run with:

    streamlit run frontend/streamlit_app.py

The app lives in the ``app/`` package, one concern per module:

    config       constants and option maps
    api_client   the only outward boundary (HTTP to the API)
    formatting   pure task -> string helpers          (unit tested)
    tasks        pure list/dict transforms            (unit tested)
    filters      Filters value object + filter bar    (parsing unit tested)
    styles       global CSS
    theme        Light / Dark / System switch
    views/       sidebar, summary and task-list rendering
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from app.api_client import APIError, fetch_todos
from app.filters import render_active_filters, render_filter_bar
from app.styles import inject_styles
from app.theme import render_theme_control, seed_theme_state
from app.views.sidebar import render_create_form
from app.views.summary import render_summary
from app.views.task_list import render_task_list

st.set_page_config(
    page_title="Task Manager",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="expanded",
)

seed_theme_state()
inject_styles()


def guarded_fetch(**query) -> list[dict]:
    """Fetch tasks, or show an error with a Retry button and stop the script."""
    try:
        return fetch_todos(**query)
    except APIError as exc:
        st.error(str(exc))
        if st.button("Retry", type="primary"):
            st.rerun()
        st.stop()


with st.sidebar:
    render_theme_control()
    st.divider()
    render_create_form()

st.title("✅ Task Manager")

render_summary(guarded_fetch())

st.header("Tasks")
filters = render_filter_bar()
shown = guarded_fetch(**filters.to_query())
render_active_filters(filters, len(shown))
render_task_list(shown, grouped=not filters.status)
