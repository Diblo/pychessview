# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Suite-local helpers for pychessview.qt integration tests."""

from __future__ import annotations

from pychessview.engine.core.primitives import Square
from tests.support.pychessview_api import board_square, piece_placement
from tests.support.pychessview_qt_api import ChessboardQtHarness


def square(file_name: str, rank: int) -> Square:
    """Return a board square from algebraic-style file and rank values.

    Args:
        file_name: Single-letter file name from ``a`` through ``h``.
        rank: One-based board rank.

    Returns:
        Square matching the requested file and rank.
    """
    return board_square(file_name, rank)


def assert_widget_piece_placement(harness: ChessboardQtHarness, expected: str) -> None:
    """Assert that a widget harness has the expected piece placement.

    Args:
        harness: Harness whose widget state should be inspected.
        expected: Expected first FEN field.
    """
    assert piece_placement(harness.widget.fen) == expected
