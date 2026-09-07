"""Unit tests for the pure component helpers (app.components.markup)."""

from app.components.markup import badge_html, truncate


# --- truncate --------------------------------------------------------------- #
def test_truncate_leaves_short_text():
    assert truncate("hello", 10) == ("hello", False)


def test_truncate_none_and_blank():
    assert truncate(None) == ("", False)
    assert truncate("   ") == ("", False)


def test_truncate_long_text_adds_ellipsis_and_flag():
    shown, cut = truncate("x" * 50, 10)
    assert cut is True
    assert len(shown) == 10 and shown.endswith("…")


def test_truncate_strips_before_measuring():
    assert truncate("  hi  ", 10) == ("hi", False)


# --- badge_html ----------------------------------------------------------- #
def test_badge_html_sets_tone_attribute():
    assert 'data-tone="warning"' in badge_html("Pending", tone="warning")


def test_badge_html_unknown_tone_falls_back_to_neutral():
    assert 'data-tone="neutral"' in badge_html("x", tone="bogus")


def test_badge_html_escapes_user_text():
    out = badge_html("<script>alert(1)</script>")
    assert "<script>" not in out and "&lt;script&gt;" in out


def test_badge_html_empty_label_is_em_dash():
    assert ">—<" in badge_html("")


def test_badge_html_icon_prefix():
    assert badge_html("Done", tone="success", icon="✓").count("✓") == 1
