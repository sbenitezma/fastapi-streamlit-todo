"""Interactive controls: a labelled segmented filter, a pager, a confirm button."""

from collections.abc import Callable
from html import escape
from typing import Any

import streamlit as st


def segmented_filter(
    label: str,
    options: dict[str, Any],
    *,
    key: str,
    default: str | None = None,
    help: str | None = None,
    collapsed: bool = True,
) -> Any:
    """A single-select segmented control that maps a label to a value.

    ``options`` is ``{visible label: value}``. Returns the value for the current
    selection; a cleared control falls back to ``default`` (or the first option).
    """
    labels = list(options)
    st.segmented_control(
        label,
        labels,
        key=key,
        selection_mode="single",
        help=help,
        label_visibility="collapsed" if collapsed else "visible",
    )
    chosen = st.session_state.get(key)
    if chosen not in options:
        chosen = default if default in options else labels[0]
    return options[chosen]


def pager(
    *, key: str, page: int, has_next: bool, on_change: Callable[[int], None]
) -> None:
    """Prev / Next controls. Renders nothing on a single first page. Buttons keep
    real labels ("Previous" / "Next") and correct ``disabled`` states."""
    if page == 0 and not has_next:
        return
    prev_col, mid, next_col = st.columns([1, 4, 1], vertical_alignment="center")
    prev_col.button(
        "‹ Previous",
        key=f"{key}-prev",
        width="stretch",
        disabled=page == 0,
        on_click=on_change,
        args=(page - 1,),
        help="Go to the previous page",
    )
    mid.markdown(
        f"<div class='tm-pageno' aria-live='polite'>Page {page + 1}</div>",
        unsafe_allow_html=True,
    )
    next_col.button(
        "Next ›",
        key=f"{key}-next",
        width="stretch",
        disabled=not has_next,
        on_click=on_change,
        args=(page + 1,),
        help="Go to the next page",
    )


def confirm_button(
    label: str,
    *,
    key: str,
    tone: str = "danger",
    title: str | None = None,
    body: str = "This can’t be undone.",
    confirm_label: str | None = None,
    help: str | None = None,
) -> bool:
    """A two-step destructive action: a popover trigger, then an explicit
    confirm. Returns ``True`` only on the run where confirm was pressed, so the
    caller keeps its own error handling around the actual side effect."""
    with st.popover(label, width="stretch", help=help):
        if title:
            st.markdown(f"{escape(label)} **{escape(title)}**?")
        st.caption(body)
        return st.button(
            confirm_label or f"Yes, {label.lower()}",
            key=f"{key}-confirm",
            type="primary" if tone == "danger" else "secondary",
            width="stretch",
        )
