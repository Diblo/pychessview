# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for promotion session behavior."""

from __future__ import annotations

import pytest

from pychessview.engine.core.annotation_types import CircleType
from pychessview.engine.core.exceptions import ChessboardViewError, MoveError
from pychessview.engine.core.primitives import Move, PieceKind, PlayerColor, Square
from pychessview.engine.layout.primitives import Coord

from ..._helpers import PromotionQueryStub, SessionAdapterStub, create_promotion_session

pytestmark = pytest.mark.unit


def test_promotion_session_show_promotion_opens_picker_and_sets_preview_move() -> None:
    """Open promotion selection only when options exist and seed the highlighted choice from the pointer."""
    adapter = SessionAdapterStub()
    query = PromotionQueryStub(index=1)
    session, _, piece_ui_state, _, promotion_state = create_promotion_session(adapter, query)
    move = Move(Square(0, 6), Square(0, 7))
    piece_ui_state.set_dragged_piece(move.from_square, Coord(1, 2))

    session.show_promotion(move, PlayerColor.WHITE, Coord(10, 20))

    assert promotion_state.is_active() is True
    assert promotion_state.move == move
    assert promotion_state.highlighted == 1
    assert piece_ui_state.preview_move == move
    assert piece_ui_state.is_dragging() is False
    assert query.calls == [(10, 20)]


def test_promotion_session_update_highlight_clears_invalid_pointer_targets() -> None:
    """Avoid leaving a stale promotion highlight when the pointer is outside valid options."""
    adapter = SessionAdapterStub()
    query = PromotionQueryStub(index=None)
    session, _, _, _, promotion_state = create_promotion_session(adapter, query)
    promotion_state.show_promotion(Move(Square(0, 6), Square(0, 7)), PlayerColor.WHITE)
    promotion_state.set_highlight(0)

    session.update_promotion_highlight(Coord(5, 6))

    assert promotion_state.highlighted is None
    assert query.calls == [(5, 6)]


def test_promotion_session_commit_applies_selected_piece_and_clears_picker_state() -> None:
    """Apply the selected promotion piece and clear all transient promotion UI state."""
    adapter = SessionAdapterStub()
    query = PromotionQueryStub(index=0)
    session, highlight_state, piece_ui_state, annotation_state, promotion_state = create_promotion_session(
        adapter, query
    )
    move = Move(Square(0, 6), Square(0, 7))
    selected_piece = promotion_state.white_promotion_pieces[0]
    promoted_move = move.with_promotion(selected_piece.kind)
    adapter.legal_promotions.append(promoted_move)
    promotion_state.show_promotion(move, PlayerColor.WHITE)
    piece_ui_state.preview_move = move
    annotation_state.add_circle(CircleType.PRIMARY, move.from_square)

    session.commit_promotion(Coord(7, 8))

    assert adapter.promotions == [promoted_move]
    assert promotion_state.is_active() is False
    assert promotion_state.highlighted is None
    assert piece_ui_state.preview_move is None
    assert annotation_state.has_annotation() is False
    assert highlight_state.get_last_move() == promoted_move
    assert query.calls == [(7, 8)]


def test_promotion_session_commit_without_valid_target_only_closes_picker() -> None:
    """Close promotion selection without mutating the game when no promotion option is targeted."""
    adapter = SessionAdapterStub()
    query = PromotionQueryStub(index=None)
    session, _, piece_ui_state, _, promotion_state = create_promotion_session(adapter, query)
    move = Move(Square(0, 6), Square(0, 7))
    promotion_state.show_promotion(move, PlayerColor.WHITE)
    piece_ui_state.preview_move = move

    session.commit_promotion(Coord(7, 8))

    assert adapter.promotions == []
    assert promotion_state.is_active() is False
    assert piece_ui_state.preview_move is None


def test_promotion_session_promote_rejects_illegal_promotion() -> None:
    """Require adapter validation before applying a promotion move."""
    adapter = SessionAdapterStub()
    query = PromotionQueryStub(index=0)
    session, _, _, _, _ = create_promotion_session(adapter, query)

    with pytest.raises(MoveError, match="legal promotion move"):
        session.promote(Move(Square(0, 6), Square(0, 7)).with_promotion(PieceKind.QUEEN))

    assert adapter.promotions == []


def test_promotion_session_close_requires_active_promotion() -> None:
    """Report invalid cleanup calls instead of silently hiding missing promotion state."""
    adapter = SessionAdapterStub()
    query = PromotionQueryStub(index=0)
    session, _, _, _, _ = create_promotion_session(adapter, query)

    with pytest.raises(ChessboardViewError, match="no promotion is active"):
        session.close_promotion()
