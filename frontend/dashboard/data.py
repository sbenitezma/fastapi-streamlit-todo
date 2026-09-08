"""Cached read layer between the views and ``api_client``.

Streamlit reruns the whole script on every interaction (theme toggle, opening a
popover, a keystroke...). Without caching, each rerun fired two HTTP requests.
``st.cache_data`` collapses reruns that don't change the data to zero network
calls; :func:`invalidate` is called after every mutation so the next rerun
refetches.
"""

import streamlit as st

from dashboard import api_client

_TTL = 10  # seconds -- bounds staleness if another client mutates


@st.cache_data(ttl=_TTL, show_spinner=False)
def load_todos(query: tuple[tuple[str, str], ...]) -> list[dict]:
    """``query`` is a sorted tuple of (key, value) pairs so it is hashable."""
    return api_client.fetch_todos(**dict(query))


@st.cache_data(ttl=_TTL, show_spinner=False)
def load_stats() -> dict:
    return api_client.fetch_stats()


def invalidate() -> None:
    load_todos.clear()
    load_stats.clear()
