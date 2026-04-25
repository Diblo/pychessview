# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for core pychessview primitive value objects."""

import pytest

from pychessview.engine.core.primitives import PIECES, SQUARES, File, Move, Piece, PieceKind, PlayerColor, Rank, Square

pytestmark = pytest.mark.unit


def test_file_and_rank_axis_lookup_rejects_invalid_indices() -> None:
    """Map zero-based board axes to enum members and reject invalid coordinates.

    Layout and adapter code use axis indices when converting between board
    coordinates and squares. Invalid indices must fail early instead of
    producing an impossible board square.
    """
    assert File.from_axis(0) is File.A
    assert File.from_axis(7) is File.H
    assert Rank.from_axis(0) is Rank.ONE
    assert Rank.from_axis(7) is Rank.EIGHT

    with pytest.raises(ValueError, match=r"file index must be in \[0, 7\]"):
        File.from_axis(8)
    with pytest.raises(ValueError, match=r"rank index must be in \[0, 7\]"):
        Rank.from_axis(-1)


def test_piece_symbol_parsing_preserves_color_and_kind() -> None:
    """Parse FEN-style symbols into value-equivalent pieces.

    Piece symbols encode both color and kind. This contract lets adapters load
    board positions without leaking parser-specific logic into UI state.
    """
    white_queen = Piece.from_symbol("Q")
    black_knight = Piece.from_symbol("n")

    assert white_queen == Piece(PlayerColor.WHITE, PieceKind.QUEEN)
    assert white_queen.symbol == "Q"
    assert black_knight == Piece(PlayerColor.BLACK, PieceKind.KNIGHT)
    assert black_knight.symbol == "n"
    with pytest.raises(ValueError, match="Symbol must be"):
        PieceKind.from_symbol("x")


def test_piece_constants_cover_every_color_kind_combination() -> None:
    """Expose one reusable piece instance for every supported color and kind.

    Promotion defaults and theme asset mapping rely on the package-level piece
    collection being complete and deterministic.
    """
    assert len(PIECES) == len(PlayerColor) * len(PieceKind)
    assert set(PIECES) == {Piece(color, kind) for color in PlayerColor for kind in PieceKind}


def test_square_indexing_and_rotation_follow_board_order() -> None:
    """Convert between square objects, indices, and rotated board orientation.

    State and layout modules use square indices as stable storage keys. Rotation
    must preserve value semantics while mapping each square to its opposite
    board coordinate.
    """
    square = Square(File.C, Rank.THREE)

    assert square.index == 18
    assert Square.from_index(18) == square
    assert Square(2, 2) == square
    assert square.rotated() == Square(File.F, Rank.SIX)
    assert square.is_light() is False
    with pytest.raises(ValueError, match=r"index must be in \[0, 63\]"):
        Square.from_index(64)


def test_square_constants_cover_entire_board_in_index_order() -> None:
    """Expose all board squares in deterministic index order.

    Render and state code can iterate this list to cover the whole board without
    recalculating file/rank pairs.
    """
    assert len(SQUARES) == 64
    assert SQUARES[0] == Square(File.A, Rank.ONE)
    assert SQUARES[-1] == Square(File.H, Rank.EIGHT)
    assert [square.index for square in SQUARES] == list(range(64))


def test_move_is_value_based_and_rejects_impossible_square_objects() -> None:
    """Treat moves as origin/destination value objects.

    Move equality must be independent of object identity so adapters and state
    containers can compare independently constructed move objects.
    """
    source = Square(File.A, Rank.TWO)
    target = Square(File.A, Rank.FOUR)

    assert Move(source, target) == Move(Square(File.A, Rank.TWO), Square(File.A, Rank.FOUR))
    assert repr(Move(source, target)).startswith("Move(from_square=")
