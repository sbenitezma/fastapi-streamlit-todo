"""AppTest coverage for the filter bar and the theme switch.

These run the Streamlit render functions in Streamlit's headless test harness
(no browser, no server) and assert on the widget tree, the returned ``Filters``
value object and the ``st.query_params`` mirroring.

``AppTest.from_function`` re-executes each script function's *source* in a fresh
module namespace, so every wrapper imports what it needs locally. The filter bar
seeds its widget state from the URL only on the first run, so a test that needs a
seeded value sets the query param *before* ``.run()``.
"""

from streamlit.testing.v1 import AppTest

from dashboard.filtering import Filters


def _qp(at, key):
    """A query param as a plain string, whichever shape AppTest hands back."""
    value = at.query_params[key]
    return value[-1] if isinstance(value, list) else value


# --- scripts run by AppTest (module-level; self-contained imports) --------- #
def _filter_bar_script() -> None:
    import streamlit as st

    from dashboard.filters import render_filter_bar

    st.session_state["result"] = render_filter_bar()


def _active_filters_script() -> None:
    from dashboard.filters import render_active_filters, render_filter_bar

    render_active_filters(render_filter_bar())


def _theme_script() -> None:
    from dashboard.theme import render_theme_control, seed_theme_state

    seed_theme_state()
    render_theme_control()


# --- filter bar --------------------------------------------------------- #
def test_filter_bar_defaults_to_no_filter():
    at = AppTest.from_function(_filter_bar_script).run()
    result: Filters = at.session_state["result"]
    assert result == Filters()
    assert not result.active
    assert [s.label for s in at.segmented_control] == ["Status"]


def test_filter_bar_seeds_from_query_params():
    at = AppTest.from_function(_filter_bar_script)
    at.query_params["status"] = "done"
    at.run()
    assert at.session_state["result"].status == "done"


def test_filter_bar_selection_updates_result_and_url():
    at = AppTest.from_function(_filter_bar_script).run()
    at.segmented_control(key="f_status").set_value("Pending").run()
    assert at.session_state["result"].status == "pending"
    assert _qp(at, "status") == "pending"


def test_clear_all_absent_without_an_active_filter():
    at = AppTest.from_function(_active_filters_script).run()
    assert "chip-clear-all" not in [b.key for b in at.button]


def test_clear_all_clears_the_active_filter():
    at = AppTest.from_function(_active_filters_script)
    at.query_params["status"] = "done"
    at.run()
    assert "chip-clear-all" in [b.key for b in at.button]

    at.button(key="chip-clear-all").click().run()
    assert at.session_state["f_status"] == "All"


# --- theme switch ----------------------------------------------------- #
def test_theme_control_defaults_to_system():
    at = AppTest.from_function(_theme_script).run()
    theme = at.segmented_control(key="tm_theme")
    assert theme.value == "System"
    assert set(theme.options) == {"System", "Light", "Dark"}


def test_theme_choice_is_mirrored_to_the_url():
    at = AppTest.from_function(_theme_script).run()
    at.segmented_control(key="tm_theme").set_value("Dark").run()
    assert _qp(at, "theme") == "Dark"
