"""Story: chip / chip_row."""

import streamlit as st

from app.components import chip, chip_row
from app.library._shell import canvas, code_block, story_header

_DEFAULT = ["Status: Pending", "Created: 2026-09-01 → …", "Assignee: me"]


def render() -> None:
    story_header(
        "chip / chip_row",
        "Removable filter tags. Sized to content, wrap when there are many.",
    )
    st.session_state.setdefault("lib_chips", list(_DEFAULT))

    def _drop(i: int) -> None:
        st.session_state["lib_chips"].pop(i)

    with canvas():
        chips = st.session_state["lib_chips"]
        if chips:
            chip_row(
                [
                    {
                        "label": lbl,
                        "key": f"lib-chip-{i}",
                        "on_remove": _drop,
                        "args": (i,),
                    }
                    for i, lbl in enumerate(chips)
                ],
                key="demo",
            )
        else:
            st.caption("edge case: empty list → renders nothing")
        if st.button("Reset chips", key="lib-chip-reset"):
            st.session_state["lib_chips"] = list(_DEFAULT)
            st.rerun()

    st.subheader("Static chip (no `on_remove`)")
    static = st.container(horizontal=True, gap="small", key="tmchips-static-demo")
    with static:
        chip("Read-only tag", key="lib-static-chip")

    code_block(
        """
from app.components import chip_row
chip_row(
    [{"label": "Status: Pending", "key": "chip-status",
      "on_remove": clear_facet, "args": ("status",)}],
    key="active",
)
"""
    )
