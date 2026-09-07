"""Component Library -- a Storybook-style browser for ``app/components``.

    streamlit run frontend/component_library.py      (or: .\\run.ps1 library)

Left sidebar = the component list; clicking one opens its isolated page with a
live canvas, controls, every state, and usage. The Light / Dark / System switch
is the same one the app uses, so the two stay visually consistent.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from app.library import (
    overview, story_badge, story_card, story_chip, story_controls,
    story_feedback, story_meter,
)
from app.styles import inject_styles
from app.theme import render_theme_control, seed_theme_state

st.set_page_config(
    page_title="Component Library",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)

seed_theme_state()
inject_styles()

nav = st.navigation(
    {
        "": [
            st.Page(overview.render, title="Overview", icon="🏠",
                    url_path="overview", default=True),
        ],
        "Primitives": [
            st.Page(story_badge.render, title="badge", icon="🏷️", url_path="badge"),
            st.Page(story_chip.render, title="chip", icon="🔖", url_path="chip"),
            st.Page(story_meter.render, title="meter", icon="📊", url_path="meter"),
        ],
        "Layout": [
            st.Page(story_card.render, title="card", icon="🗂️", url_path="card"),
        ],
        "Feedback": [
            st.Page(story_feedback.render, title="load / empty / error",
                    icon="⏳", url_path="feedback"),
        ],
        "Controls": [
            st.Page(story_controls.render, title="segmented / pager / confirm",
                    icon="🎛️", url_path="controls"),
        ],
    },
    expanded=True,
)

with st.sidebar:
    st.divider()
    render_theme_control()

nav.run()
