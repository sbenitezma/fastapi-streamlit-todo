"""Story: load / empty_state / error_state -- the three non-happy paths."""

import time

import streamlit as st

from app.components import empty_state, error_state, load, segmented_filter
from app.library._shell import canvas, code_block, story_header


def render() -> None:
    story_header(
        "load · empty_state · error_state",
        "Loading, empty and error handling in one place.",
    )

    st.subheader("load()")
    with canvas():
        outcome = segmented_filter(
            "outcome", {"succeeds": "ok", "fails": "err"},
            key="lib-load-mode", default="succeeds", collapsed=False,
        )
        if st.button("Run the fetch", key="lib-load-run"):
            def _fetch():
                time.sleep(1.2)
                if outcome == "err":
                    raise RuntimeError("The API responded 503: service unavailable")
                return [1, 2, 3]

            data = load(
                _fetch, key="lib-load", spinner="Loading…",
                error_types=(RuntimeError,),
            )
            st.success(f"got {len(data)} items")

    st.subheader("empty_state()")
    with canvas():
        empty_state(
            "No tasks yet", body="Add your first one from the sidebar.",
            icon="✅", key="lib-empty-plain",
        )
    with canvas():
        empty_state(
            "Nothing matches this view", body="Try a different filter.",
            icon="🔍", action_label="Clear all filters",
            on_action=lambda: st.toast("filters cleared"), key="lib-empty-cta",
        )

    st.subheader("error_state() — non-fatal")
    with canvas():
        error_state("Could not save — you can keep working.", key="lib-errstate")

    code_block(
        """
data = load(lambda: fetch(...), key="todos", spinner="Loading tasks…",
            error_types=(APIError,))
if not data:
    empty_state("No tasks yet", body="Add one from the sidebar.", icon="✅")
"""
    )
