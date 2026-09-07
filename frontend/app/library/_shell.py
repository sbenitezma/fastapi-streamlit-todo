"""Shared chrome for the component stories."""

from streamlit.delta_generator import DeltaGenerator
import streamlit as st


def story_header(name: str, summary: str) -> None:
    st.title(name)
    st.caption(summary)


def canvas() -> "DeltaGenerator":
    """The isolated preview area (Storybook's 'canvas')."""
    return st.container(border=True)


def controls_row() -> tuple["DeltaGenerator", "DeltaGenerator"]:
    """Two columns: a wide preview and a narrow 'controls' (args) panel."""
    preview, ctrls = st.columns([2, 1], vertical_alignment="center")
    ctrls.caption("Controls")
    return preview, ctrls


def code_block(src: str) -> None:
    st.subheader("Usage")
    st.code(src.strip("\n"), language="python")
