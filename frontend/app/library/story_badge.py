"""Story: badge / badge_html."""

import streamlit as st

from app.components import badge
from app.library._shell import canvas, code_block, controls_row, story_header

_TONES = ["neutral", "warning", "success", "danger", "info"]


def render() -> None:
    story_header(
        "badge",
        "A status pill. Colour reinforces a text label (+ optional icon) — never colour alone.",
    )

    with canvas():
        preview, ctrls = controls_row()
        tone = ctrls.selectbox("tone", _TONES, index=1)
        label = ctrls.text_input("label", "Pending")
        icon = ctrls.text_input("icon", "◷")
        with preview:
            badge(label, tone=tone, icon=icon or None)

    st.subheader("All states")
    row = st.container(horizontal=True, gap="small", wrap=True)
    for t in _TONES:
        with row:
            badge(t.title(), tone=t)
    with row:
        badge("With icon", tone="success", icon="✓")
    with row:
        badge("", tone="neutral")  # edge: empty label -> em dash
    with row:
        badge("unknown tone", tone="bogus")  # edge: falls back to neutral

    code_block(
        """
from app.components import badge
badge("Pending", tone="warning", icon="◷")

# inline, composed into a parent's single markdown call:
from app.components.markup import badge_html
st.markdown(f'<div>{title}{badge_html("Done", tone="success")}</div>',
            unsafe_allow_html=True)
"""
    )
