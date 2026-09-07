"""Landing page: what the library is + the design-token palette."""

import streamlit as st

from app.components.tokens import TONE


def render() -> None:
    st.title("🧩 Component Library")
    st.write(
        "Reusable, accessible Streamlit render functions from `app/components/`. "
        "Pick a component in the sidebar — each page has a live **canvas**, "
        "**controls**, the full set of **states**, and copy-paste **usage**."
    )

    st.subheader("Design tokens")
    st.caption(
        "Colour tokens; mirrored as `:root` custom properties in `styles.py`. "
        "Every pair meets WCAG AA (≥ 4.5:1) on any surface."
    )
    cols = st.columns(len(TONE))
    for col, (name, (bg, fg)) in zip(cols, TONE.items()):
        col.markdown(
            f"<div style='background:{bg};color:{fg};padding:0.55rem;"
            f"border-radius:6px;text-align:center;font-weight:700;"
            f"font-size:0.78rem'>{name}</div>",
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown(
        "**Conventions**, the props table and the loading / empty / error matrix "
        "live in `frontend/app/components/README.md`. "
        "The Light / Dark / System switch below is the same one the app uses."
    )
