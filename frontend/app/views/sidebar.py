"""Sidebar: the 'Add task' creation form."""

from datetime import date

import streamlit as st

from app.api_client import APIError, create_todo


def render_create_form() -> None:
    today = date.today()
    st.header("Add task")
    with st.form("new_task", clear_on_submit=True, border=False):
        title = st.text_input(
            "Title", max_chars=200, placeholder="What needs doing?", help="Required.",
        )
        description = st.text_area(
            "Description", max_chars=2000, height=80, placeholder="Optional details",
        )
        created = st.date_input(
            "Created on", value=today, max_value=today, format="YYYY-MM-DD",
            help="Defaults to today. Pick an earlier date to log a past task; "
                 "future dates are not allowed.",
        )
        submitted = st.form_submit_button("Add task", type="primary", width="stretch")

    if not submitted:
        return
    if not title.strip():
        st.warning("Title is required.")
        return
    if created > today:
        st.warning("The creation date cannot be in the future.")
        return
    try:
        create_todo(title, description, created if created != today else None)
        st.toast("Task added", icon="✅")
        st.rerun()
    except APIError as exc:
        st.error(str(exc))
