"""A bordered container with an optional coloured left edge and a muted state."""

from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:  # pragma: no cover
    from streamlit.delta_generator import DeltaGenerator


def card(
    *, accent: str | None = None, muted: bool = False, key: str = ""
) -> "DeltaGenerator":
    """Return a bordered container to render into.

    ``accent`` is a tone name ("warning", "success", …) that colours the left
    edge; ``muted`` dims the content (e.g. a completed item). Both are applied by
    CSS that matches the container's ``st-key-*`` class, so ``key`` must be
    unique per card (the caller passes e.g. the row id).

    Usage::

        with card(accent="warning", key=str(todo["id"])):
            st.write(...)
    """
    parts = ["tmcard"]
    if accent:
        parts.append(accent)
    if muted:
        parts.append("muted")
    parts.append(key or "0")
    return st.container(border=True, key="-".join(parts))
