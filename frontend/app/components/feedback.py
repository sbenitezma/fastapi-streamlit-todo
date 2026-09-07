"""Loading, error and empty states -- the three non-happy paths, in one place."""

from collections.abc import Callable
from html import escape
from typing import TypeVar

import streamlit as st

T = TypeVar("T")


def load(
    loader: Callable[[], T],
    *,
    key: str,
    spinner: str = "Loading…",
    error_types: tuple[type[BaseException], ...] = (Exception,),
) -> T:
    """Run ``loader()`` behind a spinner (only visible on a real fetch, not a
    cache hit). On ``error_types`` show the message + a Retry button and stop the
    script -- the caller can assume a value came back.
    """
    try:
        with st.spinner(spinner, show_time=True):
            return loader()
    except error_types as exc:  # noqa: BLE001 -- caller chooses the types
        st.error(str(exc), icon="⚠️")
        if st.button("Retry", key=f"{key}-retry", type="primary"):
            st.rerun()
        st.stop()


def empty_state(
    title: str,
    *,
    body: str | None = None,
    icon: str = "🗒️",
    action_label: str | None = None,
    on_action: Callable[[], None] | None = None,
    key: str = "tm-empty",
) -> None:
    """A friendly zero-data panel. Announced to screen readers (``role=status``);
    the icon is decorative (``aria-hidden``)."""
    with st.container(border=True, key=key):
        html = [
            '<div class="tm-empty" role="status">',
            f'<div class="tm-empty__icon" aria-hidden="true">{escape(icon)}</div>',
            f'<div class="tm-empty__title">{escape(title)}</div>',
        ]
        if body:
            html.append(f'<div class="tm-empty__body">{escape(body)}</div>')
        html.append("</div>")
        st.markdown("".join(html), unsafe_allow_html=True)
        if action_label and on_action:
            st.button(action_label, key=f"{key}-action", type="primary",
                      on_click=on_action)


def error_state(
    message: str, *, key: str = "tm-error", on_retry: Callable[[], None] | None = None
) -> None:
    """Standalone error box + optional Retry (for errors that don't stop the script)."""
    st.error(message, icon="⚠️")
    if on_retry and st.button("Retry", key=f"{key}-retry", type="primary"):
        on_retry()
