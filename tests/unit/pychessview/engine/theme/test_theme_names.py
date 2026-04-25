# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for theme name enums."""

import pytest

from pychessview.engine.theme.highlight_theme_name import HighlightThemeName
from pychessview.engine.theme.theme_name import ThemeName

pytestmark = pytest.mark.unit


def test_theme_name_values_match_resource_directory_names() -> None:
    """Keep built-in theme enum values aligned with package resource folders.

    Theme loading resolves enum values directly as asset directories, so value
    changes are observable runtime behavior.
    """
    assert ThemeName.DEFAULT == "default"
    assert ThemeName.STANDARD_CHESS == "default"


def test_highlight_theme_names_match_settings_keys() -> None:
    """Keep highlight enum values aligned with theme settings keys.

    Theme loading builds asset lookups from these values, and render layers use
    the enum members as stable highlight identifiers.
    """
    assert HighlightThemeName.LAST_MOVE == "last_move"
    assert HighlightThemeName.CHECK == "check"
    assert HighlightThemeName.SELECTED == "selected"
    assert HighlightThemeName.OPPONENT_SELECTED == "opponent_selected"
    assert HighlightThemeName.HINT_OCCUPIED == "hint_occupied"
