"""Light / Dark / System theme switch.

Streamlit has no runtime API to change the theme, but its own switcher just
writes the chosen name to ``localStorage`` and reloads. We drive that exact
mechanism from a 0-px helper iframe, so Streamlit themes every widget natively
(no brittle CSS overrides) and our control stays in sync with the built-in one
in the toolbar menu.

The choice is mirrored to the URL (``?theme=``) so it survives the reload the
switch triggers -- otherwise session state would reset and the sync would loop.
"""

import json

import streamlit as st
import streamlit.components.v1 as components

from app.config import THEME_CHOICES


def seed_theme_state() -> None:
    """Initialise ``tm_theme`` from the URL on first load."""
    from_url = st.query_params.get("theme", "System")
    st.session_state.setdefault(
        "tm_theme", from_url if from_url in THEME_CHOICES else "System"
    )


def _apply_theme(choice: str) -> None:
    components.html(
        f"""
        <script>
          const target = {json.dumps(choice)};
          try {{
            const ls = window.parent.localStorage;
            let key = null;
            for (let i = 0; i < ls.length; i++) {{
              if (ls.key(i).startsWith("stActiveTheme")) {{ key = ls.key(i); break; }}
            }}
            key = key || "stActiveTheme-/-v2";
            const current = JSON.parse(ls.getItem(key) || '"System"');
            if (current !== target) {{
              ls.setItem(key, JSON.stringify(target));
              window.parent.location.reload();
            }}
          }} catch (e) {{ /* localStorage blocked -- fall back to the menu switcher */ }}
        </script>
        """,
        height=0,
    )


def _theme_touched() -> None:
    st.session_state["_theme_touched"] = True


def render_theme_control() -> None:
    st.segmented_control(
        "Theme", list(THEME_CHOICES), key="tm_theme", selection_mode="single",
        on_change=_theme_touched, help="Switch between light and dark.",
    )
    choice = st.session_state.get("tm_theme") or "System"
    if st.session_state.get("_theme_touched") or "theme" in st.query_params:
        if st.query_params.get("theme") != choice:
            st.query_params["theme"] = choice
        _apply_theme(choice)
