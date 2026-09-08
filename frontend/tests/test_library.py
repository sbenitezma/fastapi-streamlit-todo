"""Import smoke test for the component-library story modules.

Catches broken imports / signature drift without a Streamlit runtime. The
rendering itself is exercised by AppTest in CI / `.\run.ps1` verification.
"""

import importlib

import pytest

_STORIES = [
    "overview",
    "story_badge",
    "story_chip",
    "story_meter",
    "story_card",
    "story_feedback",
    "story_controls",
]


@pytest.mark.parametrize("name", _STORIES)
def test_story_module_exposes_render(name):
    module = importlib.import_module(f"dashboard.library.{name}")
    assert callable(module.render)
