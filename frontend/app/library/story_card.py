"""Story: card."""

import streamlit as st

from app.components import badge_html, card
from app.library._shell import canvas, code_block, controls_row, story_header

_LONG = (
    "A deliberately very long task title that must be truncated so the card keeps "
    "a predictable height whatever the user types into the form"
)


def render() -> None:
    story_header(
        "card",
        "A bordered container with a coloured left edge and a muted state.",
    )

    with canvas():
        preview, ctrls = controls_row()
        accent = ctrls.selectbox(
            "accent", ["warning", "success", "danger", "info", "(none)"]
        )
        muted = ctrls.toggle("muted", value=False)
        with preview:
            with card(
                accent=None if accent == "(none)" else accent,
                muted=muted, key="lib-card",
            ):
                st.markdown(f'<div class="tm-title">{_LONG}</div>',
                            unsafe_allow_html=True)
                st.caption("card content")

    st.subheader("Pending vs done")
    with card(accent="warning", key="lib-card-pending"):
        st.markdown(
            f'<div class="tm-title">Ship the release'
            f'{badge_html("◷ Pending", tone="warning")}</div>',
            unsafe_allow_html=True,
        )
    with card(accent="success", muted=True, key="lib-card-done"):
        st.markdown(
            f'<div class="tm-title tm-title--done">Ship the release'
            f'{badge_html("✓ Done", tone="success")}</div>',
            unsafe_allow_html=True,
        )

    code_block(
        """
with card(accent="warning", muted=False, key=str(todo["id"])):
    st.markdown(f'<div class="tm-title">{title}</div>', unsafe_allow_html=True)
"""
    )
