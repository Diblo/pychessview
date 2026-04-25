# Copyright 2026 Diblo
# Licensed under the Apache License, Version 2.0

"""Unit tests for pychessview exception types."""

import pytest

from pychessview.engine.core.exceptions import (
    ChessboardViewError,
    LayoutError,
    MoveError,
    PieceNotFoundError,
    SquareOccupiedError,
    StateError,
    ThemeError,
    ThemeParseError,
)

pytestmark = pytest.mark.unit


def test_exception_hierarchy_preserves_catch_boundaries() -> None:
    """Keep exception subclasses grouped by their operational failure area.

    Callers can catch broad pychessview failures through ``ChessboardViewError``
    while still handling move, state, layout, and theme failures separately.
    """
    assert issubclass(MoveError, ChessboardViewError)
    assert issubclass(StateError, ChessboardViewError)
    assert issubclass(SquareOccupiedError, StateError)
    assert issubclass(PieceNotFoundError, StateError)
    assert issubclass(ThemeError, ChessboardViewError)
    assert issubclass(ThemeParseError, ThemeError)
    assert issubclass(LayoutError, ChessboardViewError)


@pytest.mark.parametrize(
    ("error_type", "message"),
    [
        (ChessboardViewError, "base"),
        (MoveError, "move"),
        (StateError, "state"),
        (SquareOccupiedError, "occupied"),
        (PieceNotFoundError, "missing"),
        (ThemeError, "theme"),
        (ThemeParseError, "parse"),
        (LayoutError, "layout"),
    ],
)
def test_exception_message_is_preserved(error_type: type[Exception], message: str) -> None:
    """Expose the caller-provided message without wrapping or rewriting it.

    The exception classes are semantic markers only. They should not alter the
    diagnostic text passed by the code that raises them.
    """
    error = error_type(message)

    assert str(error) == message
