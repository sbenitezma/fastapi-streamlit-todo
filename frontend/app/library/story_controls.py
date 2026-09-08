"""Story: segmented_filter / pager / confirm_button."""

import streamlit as st

from app.components import confirm_button, pager, segmented_filter
from app.library._shell import canvas, code_block, story_header


def render() -> None:
    story_header(
        "segmented_filter · pager · confirm_button",
        "Interactive controls: a label→value filter, pagination, a two-step delete.",
    )

    st.subheader("segmented_filter()")
    with canvas():
        value = segmented_filter(
            "Status",
            {"All": None, "Pending": "pending", "Done": "done"},
            key="lib-seg",
            default="All",
            collapsed=False,
        )
        st.write("returned value:", repr(value))

    st.subheader("pager()")
    st.session_state.setdefault("lib_page", 0)
    with canvas():
        pager(
            key="lib-pager",
            page=st.session_state["lib_page"],
            has_next=st.session_state["lib_page"] < 3,
            on_change=lambda p: st.session_state.__setitem__("lib_page", p),
        )
        st.write("page index:", st.session_state["lib_page"], "· has_next up to 3")

    st.subheader("confirm_button()")
    with canvas():
        if confirm_button("Delete", key="lib-confirm", title="Buy bread"):
            st.toast("deleted!", icon="🗑️")
        st.caption("opens a popover; returns True only on the confirm click")

    code_block(
        """
value = segmented_filter("Status", {"All": None, "Pending": "pending"},
                         key="f_status", default="All")
pager(key="pager", page=page, has_next=len(rows) == PAGE_SIZE, on_change=go_to_page)
if confirm_button("Delete", key=f"del-{tid}", title=title):
    do_delete(tid)
"""
    )
