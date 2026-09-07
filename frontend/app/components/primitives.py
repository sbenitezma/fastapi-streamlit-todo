"""Small presentational building blocks: badge, chip / chip row, meter."""

from collections.abc import Callable, Sequence
from html import escape

import streamlit as st

from app.components.markup import badge_html


def badge(label: str, *, tone: str = "neutral", icon: str | None = None) -> None:
    """Render a status pill on its own. For an inline pill (e.g. after a title)
    compose :func:`app.components.markup.badge_html` into the parent markdown."""
    st.markdown(badge_html(label, tone=tone, icon=icon), unsafe_allow_html=True)


def chip(
    label: str,
    *,
    key: str,
    on_remove: Callable[..., None] | None = None,
    args: tuple = (),
    help: str | None = None,
) -> None:
    """A filter tag. Removable (a ``✕`` button firing ``on_remove``) when given a
    callback, otherwise a static pill."""
    if on_remove is None:
        st.markdown(
            f'<span class="tm-chip tm-chip--static">{escape(label)}</span>',
            unsafe_allow_html=True,
        )
        return
    st.button(
        f"✕ {label}", key=key, type="secondary",
        on_click=on_remove, args=args,
        help=help or f"Remove filter: {label}",
    )


def chip_row(chips: Sequence[dict], *, key: str = "tm-chips") -> None:
    """Lay chips out left-to-right at their natural width, wrapping when many.

    Each item is a dict of :func:`chip` kwargs, e.g.
    ``{"label": "Status: Pending", "key": "chip-status", "on_remove": cb, "args": (…,)}``.
    """
    row = st.container(horizontal=True, gap="small", wrap=True, key=key)
    for item in chips:
        with row:
            chip(**item)


def meter(
    value: float, total: float, *, label: str | None = None, note: str | None = None
) -> None:
    """A progress bar + caption. ``note`` is appended after a middot. Edge cases:
    ``total <= 0`` shows a neutral "nothing yet" line; ``value`` clamps to
    ``[0, total]``."""
    if total <= 0:
        st.caption(f"No {label or 'items'} yet." if label else "Nothing yet.")
        return
    done = max(0, min(value, total))
    text = f"**{int(done)} of {int(total)}{f' {label}' if label else ''}**"
    if note:
        text += f" · {note}"
    st.progress(done / total, text=text)
