"""Design tokens -- the single source of truth for colour/space/radius.

The CSS mirror of these values lives in ``dashboard/styles.py`` as ``:root`` custom
properties. Keep the two in sync; the Python side is used when a component builds
inline HTML, the CSS side for everything rendered by Streamlit widgets.
"""

# tone -> (background, foreground). Self-contained pairs: they meet WCAG AA
# (>= 4.5:1) on top of *any* surface, light or dark, so a badge is legible
# wherever it lands.
TONE: dict[str, tuple[str, str]] = {
    "neutral": ("#5b616e", "#ffffff"),  # 5.6:1
    "warning": ("#8a5000", "#ffffff"),  # 7.5:1  -- "pending"
    "success": ("#0f6b3d", "#ffffff"),  # 7.0:1  -- "done"
    "danger": ("#b3261e", "#ffffff"),  # 5.9:1
    "info": ("#1c5fb8", "#ffffff"),  # 5.3:1
}

# Left-edge accent colours for cards (used via CSS :has()).
ACCENT: dict[str, str] = {
    "neutral": "#5b616e",
    "warning": "#c77800",
    "success": "#1a8a52",
    "danger": "#b3261e",
    "info": "#1c64f2",
}

SPACE = {"xs": "0.25rem", "sm": "0.5rem", "md": "0.9rem", "lg": "1.4rem"}
RADIUS = {"sm": "6px", "pill": "999px"}
