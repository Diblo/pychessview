# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for piece UI state."""

import pytest

from pychessview.engine.core.primitives import File, Move, Piece, PieceKind, PlayerColor, Rank, Square
from pychessview.engine.core.state.piece_ui_state import PieceUiState
from pychessview.engine.layout.primitives import Coord
from tests.unit.pychessview.engine._helpers import MutableAdapter

pytestmark = pytest.mark.unit


def test_piece_ui_state_reads_piece_placement_from_adapter_copy() -> None:
    """Expose adapter piece placement without leaking mutable adapter storage.

    Render layers depend on the current board position, but callers must not be
    able to mutate adapter state through the returned mapping.
    """
    adapter = MutableAdapter()
    state = PieceUiState(adapter)
    square = Square(File.D, Rank.FOUR)
    piece = Piece(PlayerColor.WHITE, PieceKind.KNIGHT)
    adapter.stored_pieces[square] = piece

    pieces = state.pieces()
    pieces.clear()

    assert state.pieces() == {square: piece}


def test_piece_ui_state_tracks_drag_position_and_preview_move() -> None:
    """Store drag origin, pointer position, and preview move independently.

    Drag rendering needs both the original square and the current pointer
    position, while move preview can be cleared without losing drag state.
    """
    state = PieceUiState(MutableAdapter())
    square = Square(File.H, Rank.EIGHT)
    start = Coord(12, 13)
    updated = Coord(14, 15)
    move = Move(square, Square(File.G, Rank.SEVEN))

    assert state.is_dragging() is False

    state.set_dragged_piece(square, start)
    state.set_dragged_position(updated)
    state.preview_move = move

    assert state.dragged_square == square
    assert state.dragged_position == updated
    assert state.preview_move == move
    assert state.is_dragging() is True


def test_piece_ui_state_clear_all_removes_transient_drag_and_preview_state() -> None:
    """Return all interaction-only piece state to an empty baseline.

    Resetting board interaction must remove both drag state and preview moves so
    the next render frame does not show stale pointer feedback.
    """
    state = PieceUiState(MutableAdapter())
    square = Square(File.A, Rank.ONE)

    state.set_dragged_piece(square, Coord(1, 2))
    state.preview_move = Move(square, Square(File.A, Rank.TWO))
    state.clear_all()

    assert state.dragged_square is None
    assert state.dragged_position is None
    assert state.preview_move is None
    assert state.is_dragging() is False
