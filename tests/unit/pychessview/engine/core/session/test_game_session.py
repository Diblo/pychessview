# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for game session behavior."""

from __future__ import annotations

import pytest

from pychessview.engine.core.annotation_types import CircleType
from pychessview.engine.core.exceptions import MoveError, PieceNotFoundError, SquareOccupiedError
from pychessview.engine.core.highlight_types import HighlightPlayer, HintStyle
from pychessview.engine.core.primitives import Move, Piece, PieceKind, PlayerColor, Square
from pychessview.engine.layout.primitives import Coord

from ..._helpers import SessionAdapterStub, create_game_session

pytestmark = pytest.mark.unit


def test_game_session_load_fen_clears_transient_state_and_preserves_requested_last_move() -> None:
    """Reset all transient UI/session state when replacing the current board position."""
    adapter = SessionAdapterStub()
    session, highlight_state, piece_ui_state, annotation_state, promotion_state = create_game_session(adapter)
    last_move = Move(Square(1, 1), Square(1, 2))
    piece_ui_state.set_dragged_piece(Square(0, 0), Coord(10, 20))
    annotation_state.add_circle(CircleType.PRIMARY, Square(0, 0))
    highlight_state.set_selected(HighlightPlayer.PLAYER, Square(0, 0))
    highlight_state.set_hints(HighlightPlayer.PLAYER, ((HintStyle.HINT, Square(1, 0)),))
    promotion_state.show_promotion(Move(Square(0, 6), Square(0, 7)), PlayerColor.WHITE)

    session.load_fen("new fen", last_move)

    assert adapter.fen == "new fen"
    assert highlight_state.get_last_move() == last_move
    assert highlight_state.get_selected() is None
    assert highlight_state.get_hints() == ()
    assert annotation_state.has_annotation() is False
    assert promotion_state.is_active() is False
    assert piece_ui_state.is_dragging() is False


def test_game_session_add_piece_rejects_occupied_square_without_mutating_board() -> None:
    """Prevent callers from overwriting existing pieces through the add-piece path."""
    adapter = SessionAdapterStub()
    square = Square(0, 0)
    existing_piece = Piece(PlayerColor.WHITE, PieceKind.KING)
    adapter.placement[square] = existing_piece
    session, _, _, _, _ = create_game_session(adapter)

    with pytest.raises(SquareOccupiedError, match="occupied square"):
        session.add_piece(square, Piece(PlayerColor.BLACK, PieceKind.QUEEN))

    assert adapter.placement == {square: existing_piece}


def test_game_session_remove_piece_rejects_empty_square_without_mutating_board() -> None:
    """Report missing pieces before clearing interaction state or changing adapter placement."""
    adapter = SessionAdapterStub()
    session, _, _, _, _ = create_game_session(adapter)

    with pytest.raises(PieceNotFoundError, match="empty square"):
        session.remove_piece(Square(0, 0))

    assert adapter.placement == {}


def test_game_session_move_requires_adapter_legal_move_before_mutating_board() -> None:
    """Reject illegal moves at the session boundary without applying adapter side effects."""
    adapter = SessionAdapterStub()
    move = Move(Square(0, 1), Square(0, 2))
    adapter.placement[move.from_square] = Piece(PlayerColor.WHITE, PieceKind.PAWN)
    session, _, _, _, _ = create_game_session(adapter)

    with pytest.raises(MoveError, match="not a legal move"):
        session.move(move)

    assert adapter.applied_moves == []
    assert adapter.placement == {move.from_square: Piece(PlayerColor.WHITE, PieceKind.PAWN)}


def test_game_session_move_applies_legal_move_and_clears_transient_state() -> None:
    """Commit a legal move, reset transient UI state, and highlight the committed move."""
    adapter = SessionAdapterStub()
    move = Move(Square(0, 1), Square(0, 2))
    pawn = Piece(PlayerColor.WHITE, PieceKind.PAWN)
    adapter.placement[move.from_square] = pawn
    adapter.legal_moves.append(move)
    session, highlight_state, piece_ui_state, annotation_state, promotion_state = create_game_session(adapter)
    piece_ui_state.set_dragged_piece(move.from_square, Coord(5, 6))
    annotation_state.add_circle(CircleType.PRIMARY, move.from_square)
    promotion_state.set_highlight(0)

    session.move(move)

    assert adapter.applied_moves == [move]
    assert adapter.placement == {move.to_square: pawn}
    assert highlight_state.get_last_move() == move
    assert annotation_state.has_annotation() is False
    assert promotion_state.highlighted is None
    assert piece_ui_state.is_dragging() is False


def test_game_session_reset_uses_default_fen_for_blank_input() -> None:
    """Treat blank reset input as a request for the adapter default position."""
    adapter = SessionAdapterStub()
    session, highlight_state, _, _, _ = create_game_session(adapter)
    highlight_state.set_last_move(Move(Square(0, 0), Square(0, 1)))

    session.reset(" ")

    assert adapter.fen == "default fen"
    assert highlight_state.get_last_move() is None
