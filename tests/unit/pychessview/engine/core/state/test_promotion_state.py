# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for promotion state."""

import pytest

from pychessview.engine.core.exceptions import StateError
from pychessview.engine.core.primitives import File, Move, Piece, PieceKind, PlayerColor, Rank, Square
from pychessview.engine.core.state.promotion_state import PromotionState

from ..._helpers import black_promotion_pieces, white_promotion_pieces

pytestmark = pytest.mark.unit


def test_promotion_state_tracks_active_move_color_and_highlight() -> None:
    """Expose the active promotion flow until it is explicitly cleared.

    Promotion rendering and release handling both rely on the same move, color,
    and highlighted option being preserved while the chooser is visible.
    """
    state = PromotionState(white_promotion_pieces(), black_promotion_pieces())
    move = Move(Square(File.A, Rank.SEVEN), Square(File.A, Rank.EIGHT))

    state.show_promotion(move, PlayerColor.WHITE)
    state.set_highlight(2)

    assert state.is_active() is True
    assert state.move == move
    assert state.color is PlayerColor.WHITE
    assert state.highlighted == 2
    assert state.is_valid_index(0) is True
    assert state.get_piece(0) == Piece(PlayerColor.WHITE, PieceKind.QUEEN)


def test_promotion_state_uses_color_specific_piece_sets() -> None:
    """Resolve promotion choices from the piece set for the active color.

    The same promotion index can represent different colored pieces, so the
    active promotion color determines which configured tuple is queried.
    """
    state = PromotionState(white_promotion_pieces(), black_promotion_pieces())
    move = Move(Square(File.H, Rank.TWO), Square(File.H, Rank.ONE))
    state.white_promotion_pieces = (Piece(PlayerColor.WHITE, PieceKind.ROOK),)
    state.black_promotion_pieces = (Piece(PlayerColor.BLACK, PieceKind.BISHOP),)

    state.show_promotion(move, PlayerColor.BLACK)

    assert state.white_promotion_pieces == (Piece(PlayerColor.WHITE, PieceKind.ROOK),)
    assert state.black_promotion_pieces == (Piece(PlayerColor.BLACK, PieceKind.BISHOP),)
    assert state.is_valid_index(1) is False
    assert state.get_piece(0) == Piece(PlayerColor.BLACK, PieceKind.BISHOP)


def test_promotion_state_rejects_invalid_choice_counts_and_target_ranks() -> None:
    """Reject promotion configuration and moves outside the supported contract.

    Promotion lists are bounded by the board UI, and promotion overlays are only
    valid on a back rank.
    """
    with pytest.raises(StateError, match="between 0 and 8"):
        PromotionState(tuple(Piece(PlayerColor.WHITE, PieceKind.QUEEN) for _ in range(9)), black_promotion_pieces())

    state = PromotionState(white_promotion_pieces(), black_promotion_pieces())
    with pytest.raises(StateError, match="rank must be 1 or 8"):
        state.show_promotion(Move(Square(File.A, Rank.TWO), Square(File.A, Rank.THREE)), PlayerColor.WHITE)


def test_promotion_state_clear_methods_have_targeted_scope() -> None:
    """Clear highlight state independently from active promotion visibility.

    Pointer movement can leave a promotion active while removing only hover
    feedback; full cleanup must then clear both active state and highlight.
    """
    state = PromotionState(white_promotion_pieces(), black_promotion_pieces())
    move = Move(Square(File.B, Rank.SEVEN), Square(File.B, Rank.EIGHT))

    state.show_promotion(move, PlayerColor.WHITE)
    state.set_highlight(1)
    state.clear_highlight()
    assert state.highlighted is None
    assert state.is_active() is True

    state.set_highlight(3)
    state.clear_all()
    assert state.is_active() is False
    assert state.highlighted is None
