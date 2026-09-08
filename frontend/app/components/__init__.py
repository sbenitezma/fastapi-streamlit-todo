"""Reusable, accessible, production-ready UI components for the dashboard.

These are Streamlit *render functions*, not web components. Conventions:

* The primary data is positional; everything else is keyword-only.
* ``key`` is required wherever the component owns interactive widgets.
* Pure-state changes use Streamlit ``on_click`` / ``on_change`` callbacks (they
  run before the rerun, so they can safely mutate widget state). Actions with
  I/O return the user's intent instead, so the caller keeps error handling.
* Long text is truncated with the full value kept in ``title`` / ``help``.
* Colour never carries meaning alone; every state also has text and/or an icon.
* Layout uses wrapping flow / column primitives so it degrades on narrow screens.

See ``app/components/README.md`` for the full reference and
``frontend/component_library.py`` for every component in every state.
"""

from app.components.card import card
from app.components.controls import confirm_button, pager, segmented_filter
from app.components.feedback import empty_state, error_state, load
from app.components.markup import badge_html, truncate
from app.components.primitives import badge, chip, chip_row, meter

__all__ = [
    "badge",
    "badge_html",
    "card",
    "chip",
    "chip_row",
    "confirm_button",
    "empty_state",
    "error_state",
    "load",
    "meter",
    "pager",
    "segmented_filter",
    "truncate",
]
