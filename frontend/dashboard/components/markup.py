"""Pure HTML builders shared by the components. No Streamlit, no I/O -> unit tested.

These return strings so they can be composed into a parent's single
``st.markdown`` call (e.g. an inline title + badge), instead of each forcing its
own block.
"""

from html import escape

_TONES = {"neutral", "warning", "success", "danger", "info"}


def truncate(text: str | None, limit: int = 140) -> tuple[str, bool]:
    """Return ``(shown, was_truncated)``. ``None`` -> ``("", False)``."""
    text = (text or "").strip()
    if len(text) <= limit:
        return text, False
    return text[: max(1, limit - 1)].rstrip() + "…", True


def badge_html(label: str, *, tone: str = "neutral", icon: str | None = None) -> str:
    """A status pill. ``tone`` drives the colour (via a ``data-tone`` attribute
    the CSS reads); an empty label renders as an em dash."""
    tone = tone if tone in _TONES else "neutral"
    text = escape((label or "").strip()) or "—"
    prefix = f"{escape(icon)} " if icon else ""
    return f'<span class="tm-badge" data-tone="{tone}">{prefix}{text}</span>'
