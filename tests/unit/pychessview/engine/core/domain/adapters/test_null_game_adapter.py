# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for the null game adapter."""

import pytest

from pychessview.engine.core.domain.adapters.null_game_adapter import NullGameAdapter
from pychessview.engine.core.primitives import File, Move, Piece, PieceKind, PlayerColor, Rank, Square

pytestmark = pytest.mark.unit


def test_null_game_adapter_tracks_fen_and_piece_mutation_without_validation() -> None:
    """Store simple board state while intentionally skipping chess legality.

    The null adapter is a lightweight fallback for tests and non-rule-aware
    flows, so moves mutate stored pieces without validating game rules.
    """
    adapter = NullGameAdapter("default fen")
    square = Square(File.A, Rank.ONE)
    move = Move(square, Square(File.A, Rank.TWO)).with_promotion(PieceKind.ROOK)
    queen = Piece(PlayerColor.WHITE, PieceKind.QUEEN)
    rook = Piece(PlayerColor.WHITE, PieceKind.ROOK)

    adapter.default_fen = "reset fen"
    adapter.set_piece(square, queen)
    adapter.move(move)

    assert adapter.default_fen == "reset fen"
    assert adapter.fen == "default fen"
    assert adapter.piece_at(square) is None
    assert adapter.piece_at(move.to_square) == rook
    assert adapter.pieces() == {move.to_square: rook}


def test_null_game_adapter_clears_manual_pieces_when_fen_is_replaced() -> None:
    """Treat FEN assignment as a position reset instead of parsing board data.

    Since the null adapter does not parse FEN strings, assigning a new FEN must
    clear manual piece placement to avoid mixing unrelated positions.
    """
    adapter = NullGameAdapter("default fen")
    square = Square(File.H, Rank.EIGHT)
    adapter.set_piece(square, Piece(PlayerColor.BLACK, PieceKind.KING))

    adapter.fen = "new fen"

    assert adapter.fen == "new fen"
    assert adapter.pieces() == {}


def test_null_game_adapter_returns_empty_or_false_defaults_for_rule_queries() -> None:
    """Report neutral rule data for every chess-specific query.

    The null adapter deliberately does not calculate turn, legality, check,
    checkmate, move history, or hints beyond stable empty defaults.
    """
    adapter = NullGameAdapter("default fen")
    move = Move(Square(File.A, Rank.ONE), Square(File.A, Rank.TWO))

    assert adapter.turn is PlayerColor.WHITE
    assert adapter.has_move_history() is False
    assert adapter.move_history == ()
    assert adapter.is_legal_move(move) is False
    assert adapter.is_promotion_move(move) is False
    assert adapter.get_legal_hints(move.from_square) == set()
    assert adapter.get_pseudo_legal_hints(move.from_square, PlayerColor.BLACK) == set()
    assert adapter.is_check() is False
    assert adapter.is_checkmate() is False
    assert adapter.king(PlayerColor.WHITE) is None
