# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for highlight type enums."""

import pytest

from pychessview.engine.core.highlight_types import HighlightPlayer, HintStyle

pytestmark = pytest.mark.unit


def test_highlight_type_values_match_layout_and_theme_contracts() -> None:
    """Keep highlight enum values stable for state, layout, and theme lookup.

    Highlight state stores the owner and hint style by enum. The string values
    are part of the contract that connects interaction state to rendered theme
    assets.
    """
    assert HighlightPlayer.PLAYER.value == "player"
    assert HighlightPlayer.OPPONENT.value == "opponent"
    assert [member.value for member in HintStyle] == ["hint", "occupied", "pseudo_hint", "pseudo_occupied"]
