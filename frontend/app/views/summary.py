"""Summary: a single compact progress line above the task list."""

import streamlit as st

from app.tasks import summarize


def render_summary(todos: list[dict]) -> None:
    total, done, pending = summarize(todos)
    if total:
        st.progress(
            done / total,
            text=f"**{done} of {total} done** · {pending} pending",
        )
    else:
        st.caption("No tasks yet — add your first one from the sidebar.")
