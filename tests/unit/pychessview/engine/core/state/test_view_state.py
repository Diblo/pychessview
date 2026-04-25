# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for view state."""

import pytest

from pychessview.engine.core.label_types import FileLabelSide, RankLabelSide
from pychessview.engine.core.primitives import PlayerColor
from pychessview.engine.core.state.view_state import ViewState

pytestmark = pytest.mark.unit


def test_view_state_stores_defaults_and_syncs_board_direction() -> None:
    """Keep orientation flags aligned with the selected player color.

    The board direction is derived from ``player``. Changing the player should
    update ``white_at_bottom`` even though the flag is stored as view state.
    """
    state = ViewState(player=PlayerColor.WHITE)

    assert state.player is PlayerColor.WHITE
    assert state.restrict_to_player_pieces is True
    assert state.restrict_to_select_opponent_pieces is False
    assert state.show_player_hints is True
    assert state.show_opponent_hints is True
    assert state.annotations_enabled is True
    assert state.show_border is True
    assert state.stretch_to_fit is False
    assert state.white_at_bottom is True
    assert state.show_labels is True
    assert state.rotate_labels is False

    state.player = PlayerColor.BLACK
    assert state.white_at_bottom is False


def test_view_state_updates_label_side_visibility_in_bulk_and_individually() -> None:
    """Allow callers to update edge label visibility without replacing all sides.

    Bulk updates accept ``None`` as "leave unchanged", while single-side updates
    target exactly one file or rank edge.
    """
    state = ViewState(player=PlayerColor.BLACK)

    state.set_sides_visibility(top=True, right=None, bottom=False, left=None)
    assert state.is_label_side_visible(FileLabelSide.TOP) is True
    assert state.is_label_side_visible(RankLabelSide.RIGHT) is False
    assert state.is_label_side_visible(FileLabelSide.BOTTOM) is False
    assert state.is_label_side_visible(RankLabelSide.LEFT) is True

    state.set_side_visibility(RankLabelSide.RIGHT, True)
    state.set_side_visibility(FileLabelSide.BOTTOM, True)

    assert state.label_side_visibility == (True, True, True, True)
