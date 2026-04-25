# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for board coordinate queries."""

import pytest

from pychessview.engine.core.primitives import File, Move, PlayerColor, Rank, Square
from pychessview.engine.core.state.view_state import ViewState

from ..._helpers import create_board_query, query_promotion_state

pytestmark = pytest.mark.unit


def test_board_query_maps_viewport_coordinates_to_squares() -> None:
    """Translate rendered board coordinates back into core square identities.

    Input controllers depend on this mapping to convert pointer events into
    board-space selection, move, annotation, and promotion operations.
    """
    query = create_board_query()

    assert query.square_at(5, 75) == Square(File.A, Rank.ONE)
    assert query.square_at(75, 5) == Square(File.H, Rank.EIGHT)
    assert query.square_at(-1, 0) is None
    assert query.is_inside(0, 0) is True
    assert query.is_inside(80, 80) is False


def test_board_query_rotates_square_mapping_when_black_is_at_bottom() -> None:
    """Mirror square lookup when the board orientation is rotated.

    A physical bottom-left click maps to ``h8`` when black is displayed at the
    bottom, preserving board-relative interaction semantics.
    """
    query = create_board_query(ViewState(PlayerColor.BLACK, show_border=False, stretch_to_fit=True))

    assert query.square_at(5, 75) == Square(File.H, Rank.EIGHT)
    assert query.square_at(75, 5) == Square(File.A, Rank.ONE)


def test_board_query_returns_promotion_index_for_active_file_only() -> None:
    """Resolve promotion choices only on the active promotion file.

    Promotion overlays occupy squares along the destination file, so coordinates
    on other files or beyond configured choices must not return an index.
    """
    promotion_state = query_promotion_state()
    promotion_state.show_promotion(Move(Square(File.A, Rank.SEVEN), Square(File.A, Rank.EIGHT)), PlayerColor.WHITE)
    query = create_board_query(promotion_state=promotion_state)

    assert query.promotion_index_at(5, 5) == 0
    assert query.promotion_index_at(5, 15) == 1
    assert query.promotion_index_at(15, 5) is None
    assert query.promotion_index_at(5, 25) is None


def test_board_query_ignores_promotion_coordinates_when_no_promotion_is_active() -> None:
    """Return no promotion index outside an active promotion flow.

    Pointer movement over a promotion file should not produce promotion indexes
    unless the promotion session has explicitly activated the chooser.
    """
    query = create_board_query()

    assert query.promotion_index_at(5, 5) is None
