"""The inline filter bar and active-filter chips (Streamlit).

The pure ``Filters`` value object and query parsing live in ``app.filtering``.
These functions draw the widgets and keep the selection mirrored in
``st.query_params`` so a filtered view is shareable and survives a reload.
"""

import streamlit as st

from app.config import DATE_FIELD_OPTIONS, STATUS_OPTIONS
from app.filtering import DATE_FIELD_LABEL, STATUS_LABEL, Filters, filters_from_query

_QUERY_KEYS = ("status", "date_field", "date_from", "date_to")


def _seed_widget_state() -> None:
    if st.session_state.get("_filters_seeded"):
        return
    seed = filters_from_query(st.query_params)
    st.session_state.setdefault("f_status", STATUS_LABEL[seed.status])
    st.session_state.setdefault("f_field", DATE_FIELD_LABEL[seed.date_field])
    st.session_state.setdefault("f_from", seed.date_from)
    st.session_state.setdefault("f_to", seed.date_to)
    st.session_state["_filters_seeded"] = True


def _current_filters() -> Filters:
    return Filters(
        status=STATUS_OPTIONS.get(st.session_state.get("f_status", "All")),
        date_field=DATE_FIELD_OPTIONS.get(
            st.session_state.get("f_field", "Created"), "created"
        ),
        date_from=st.session_state.get("f_from"),
        date_to=st.session_state.get("f_to"),
    )


def _sync_query_params(filters: Filters) -> None:
    desired = filters.to_query()
    for key in _QUERY_KEYS:
        if key in desired:
            if st.query_params.get(key) != desired[key]:
                st.query_params[key] = desired[key]
        elif key in st.query_params:
            del st.query_params[key]


def _clear_facet(facet: str) -> None:
    if facet in ("status", "all"):
        st.session_state["f_status"] = "All"
    if facet in ("dates", "all"):
        st.session_state["f_field"] = "Created"
        st.session_state["f_from"] = None
        st.session_state["f_to"] = None


def render_filter_bar() -> Filters:
    """Inline status control + a 'Filters' popover for the date range."""
    _seed_widget_state()

    left, right = st.columns([3, 1], vertical_alignment="center")
    with left:
        st.segmented_control(
            "Status", list(STATUS_OPTIONS), key="f_status",
            selection_mode="single", label_visibility="collapsed",
        )
    with right:
        # the badge reflects only what the popover contains (the date range)
        label = "Filters (1)" if _current_filters().date_range_active else "Filters"
        with st.popover(label, width="stretch"):
            st.selectbox(
                "Date field", list(DATE_FIELD_OPTIONS), key="f_field",
                help="Which timestamp the range applies to.",
            )
            c_from, c_to = st.columns(2)
            c_from.date_input("From", value=None, format="YYYY-MM-DD", key="f_from")
            c_to.date_input("To", value=None, format="YYYY-MM-DD", key="f_to")
            d_from, d_to = st.session_state.get("f_from"), st.session_state.get("f_to")
            if d_from and d_to and d_from > d_to:
                st.warning("“From” is later than “To”.")

    filters = _current_filters()
    _sync_query_params(filters)
    return filters


def render_active_filters(filters: Filters, shown_count: int) -> None:
    """Count line plus one removable chip per active facet."""
    st.caption(f"{shown_count} shown" + (" · filtered" if filters.active else ""))
    if not filters.active:
        return

    chips = filters.chips()
    st.markdown('<div class="tm-chips">', unsafe_allow_html=True)
    cols = st.columns(len(chips) + 1, vertical_alignment="center")
    for col, (facet, chip_label) in zip(cols, chips):
        col.button(
            f"✕ {chip_label}", key=f"chip-{facet}", on_click=_clear_facet,
            args=(facet,), help="Remove this filter",
        )
    cols[-1].button(
        "Clear all", key="chip-clear-all", type="primary",
        on_click=_clear_facet, args=("all",),
    )
    st.markdown("</div>", unsafe_allow_html=True)
