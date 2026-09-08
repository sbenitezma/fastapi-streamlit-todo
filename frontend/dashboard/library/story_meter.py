"""Story: meter."""

import streamlit as st

from dashboard.components import meter
from dashboard.library._shell import canvas, code_block, controls_row, story_header


def render() -> None:
    story_header(
        "meter",
        "Progress bar + caption. Clamps value to [0, total]; total ≤ 0 → a neutral 'nothing yet' line.",
    )

    with canvas():
        preview, ctrls = controls_row()
        total = ctrls.slider("total", 0, 20, 10)
        value = ctrls.slider("value", 0, 20, 3)
        label = ctrls.text_input("label", "done")
        note = ctrls.text_input("note", "7 pending")
        with preview:
            meter(value, total, label=label or None, note=note or None)

    st.subheader("Edge cases")
    st.caption("typical")
    meter(3, 10, label="done", note="7 pending")
    st.caption("total = 0")
    meter(0, 0, label="tasks")
    st.caption("value > total → clamped to a full bar")
    meter(14, 10, label="done")

    code_block(
        'meter(stats["done"], stats["total"], label="done", '
        "note=f\"{stats['pending']} pending\")"
    )
