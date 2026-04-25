# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for the python-chess adapter."""

import pytest

from pychessview.engine.core.domain.adapters.python_chess_adapter import PythonChessGameAdapter
from pychessview.engine.core.primitives import File, Move, Piece, PieceKind, PlayerColor, Rank, Square

pytestmark = [pytest.mark.unit, pytest.mark.requires_python_chess]


def test_python_chess_adapter_loads_fen_and_exposes_piece_mapping() -> None:
    """Translate python-chess board state into core piece primitives.

    The adapter boundary must expose fresh core objects keyed by core squares,
    not python-chess internals.
    """
    adapter = PythonChessGameAdapter("8/8/8/8/8/8/8/K6k w - - 0 1")

    assert adapter.turn is PlayerColor.WHITE
    assert adapter.piece_at(Square(File.A, Rank.ONE)) == Piece(PlayerColor.WHITE, PieceKind.KING)
    assert adapter.piece_at(Square(File.H, Rank.ONE)) == Piece(PlayerColor.BLACK, PieceKind.KING)
    assert adapter.king(PlayerColor.WHITE) == Square(File.A, Rank.ONE)
    assert adapter.pieces()[Square(File.A, Rank.ONE)] == Piece(PlayerColor.WHITE, PieceKind.KING)


def test_python_chess_adapter_validates_normal_and_promotion_moves() -> None:
    """Require promotion kinds only for legal promotion moves.

    Promotion legality depends on both the move and selected promotion kind,
    while normal legal moves must reject an unexpected promotion argument.
    """
    adapter = PythonChessGameAdapter("8/P7/8/8/8/8/8/K6k w - - 0 1")
    promotion_move = Move(Square(File.A, Rank.SEVEN), Square(File.A, Rank.EIGHT))
    promotion_piece = Piece(PlayerColor.WHITE, PieceKind.QUEEN)
    promoted_move = promotion_move.with_promotion(PieceKind.QUEEN)

    assert adapter.is_promotion_move(promotion_move) is True
    assert adapter.is_legal_move(promotion_move) is False
    assert adapter.is_legal_move(promoted_move) is True
    assert adapter.is_legal_move(promotion_move.with_promotion(PieceKind.KING)) is False
    assert adapter.is_legal_move(promotion_move.with_promotion(PieceKind.PAWN)) is False

    adapter.move(promoted_move)

    assert adapter.move_history == (promoted_move,)
    assert adapter.piece_at(promoted_move.to_square) == promotion_piece


def test_python_chess_adapter_records_moves_and_legal_hints() -> None:
    """Expose move history and legal hints through core move and square types.

    Controller selection uses legal-hint sets, and game sessions use move
    history to refresh the last-move highlight after a move is applied.
    """
    adapter = PythonChessGameAdapter("8/8/8/8/8/8/4P3/K6k w - - 0 1")
    move = Move(Square(File.E, Rank.TWO), Square(File.E, Rank.FOUR))

    assert Square(File.E, Rank.THREE) in adapter.get_legal_hints(move.from_square)
    assert Square(File.E, Rank.FOUR) in adapter.get_legal_hints(move.from_square)

    adapter.move(move)

    assert adapter.has_move_history() is True
    assert adapter.move_history == (move,)
    assert adapter.piece_at(move.to_square) == Piece(PlayerColor.WHITE, PieceKind.PAWN)
